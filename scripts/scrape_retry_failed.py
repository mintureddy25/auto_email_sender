"""
One-off retry: re-runs only the queries that failed in the last scrape due to
Apify monthly limit on TOKEN_11 — the three "hiring SDE" queries (Pune/
Bangalore/Hyderabad) and the people_search scraper. Uses the new APIFY_TOKEN
from .env (TOKEN_12) which has full $5 credit.

Usage:
    python3 scripts/scrape_retry_failed.py
"""

import _bootstrap  # noqa: F401

from datetime import datetime

from apify_client import ApifyClient

import src.config as cfg
from src.config import APIFY_TOKEN
from src.utils.file_utils import load_json, save_json
from src.queue.rabbitmq import publish_batch
from src.scrapers.base import ScrapeResult, SeenSet
from src.collectors import get_all as get_types

# Override the query list before importing scrapers (hiring_posts imports it at module load)
cfg.HIRING_POST_QUERIES = [
    "hiring SDE Pune",
    "hiring SDE Bangalore",
    "hiring SDE Hyderabad",
]

from src.scrapers.hiring_posts import HiringPostsScraper
from src.scrapers.people_search import PeopleSearchScraper
import src.scrapers.hiring_posts as hp_mod
hp_mod.HIRING_POST_QUERIES = cfg.HIRING_POST_QUERIES


def main():
    print("=" * 60)
    print(f"  RETRY FAILED QUERIES - {datetime.now()}")
    print("=" * 60)
    print(f"  Hiring queries: {cfg.HIRING_POST_QUERIES}")

    types = get_types()
    seen = SeenSet()
    for t in types:
        for key in t.load_seen():
            seen.add(t.name, key)
    summary_seen = ", ".join(f"{t.name}={seen.count(t.name)}" for t in types)
    print(f"Already processed: {summary_seen}")

    apify = ApifyClient(APIFY_TOKEN)
    combined = ScrapeResult()

    for ScraperCls in (HiringPostsScraper, PeopleSearchScraper):
        scraper = ScraperCls(apify)
        try:
            combined.merge(scraper.run(seen))
        except Exception as e:
            print(f"[{scraper.name}] fatal error: {e}")

    for t in types:
        items = combined.get(t.name)
        if not items:
            continue
        stored = load_json(t.storage_file)
        stored.extend(items)
        save_json(t.storage_file, stored)

    print("\n" + "=" * 60)
    for t in types:
        items = combined.get(t.name)
        if items and t.queue_name:
            publish_batch(t, items)

    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    for t in types:
        print(f"  {t.name:15s} {combined.count(t.name)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
