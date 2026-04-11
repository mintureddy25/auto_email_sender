"""
Cron entry: runs every registered scraper in src/scrapers/, persists
results per DataType, and publishes to each type's queue (if any).

Add a new scraper: drop a file in src/scrapers/.
Add a new data type: drop a file in src/collectors/.
Add a new sender: drop a file in src/senders/.
No edits here needed.
"""

from datetime import datetime

from apify_client import ApifyClient

from src.config import APIFY_TOKEN
from src.utils.file_utils import load_json, save_json
from src.queue.rabbitmq import publish_batch
from src.scrapers import get_all as get_scrapers
from src.scrapers.base import ScrapeResult, SeenSet
from src.collectors import get_all as get_types


def main():
    print("=" * 60)
    print(f"  AUTO SCRAPER - {datetime.now()}")
    print("=" * 60)

    types = get_types()
    print(f"Data types: {[t.name for t in types]}")

    # Load dedup set per type
    seen = SeenSet()
    for t in types:
        for key in t.load_seen():
            seen.add(t.name, key)
    summary_seen = ", ".join(f"{t.name}={seen.count(t.name)}" for t in types)
    print(f"Already processed: {summary_seen}")

    # Run every registered scraper
    apify = ApifyClient(APIFY_TOKEN)
    combined = ScrapeResult()
    scrapers = get_scrapers()
    print(f"Registered scrapers: {[s.name for s in scrapers]}")

    for ScraperCls in scrapers:
        scraper = ScraperCls(apify)
        try:
            combined.merge(scraper.run(seen))
        except Exception as e:
            print(f"[{scraper.name}] fatal error: {e}")

    # Persist every type that got new items
    for t in types:
        items = combined.get(t.name)
        if not items:
            continue
        stored = load_json(t.storage_file)
        stored.extend(items)
        save_json(t.storage_file, stored)

    # Publish to queue for every type that has a queue_name
    print("\n" + "=" * 60)
    for t in types:
        items = combined.get(t.name)
        if items and t.queue_name:
            publish_batch(t, items)

    # Summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    for t in types:
        print(f"  {t.name:15s} {combined.count(t.name)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
