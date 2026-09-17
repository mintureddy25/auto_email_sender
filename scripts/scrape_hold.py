"""
Run hiring_posts only, persist new items to data files, but DO NOT publish
to RabbitMQ. New items pile up in `data/pending_queue.json`. Run
`drain_pending.py` later (e.g. Monday morning) to publish them.

Why hold? E.g. scraping on a weekend when recruiters won't read mail until
Monday — we still want fresh posts captured before they fall off LinkedIn,
just don't want to fire emails into the void.

Usage:
    python3 scripts/scrape_hold.py
"""

import _bootstrap  # noqa: F401

import json
from datetime import datetime
from pathlib import Path

from apify_client import ApifyClient

from src.config import APIFY_TOKEN, PENDING_QUEUE_FILE
from src.utils.file_utils import load_json, save_json
from src.scrapers.base import ScrapeResult, SeenSet
from src.scrapers.hiring_posts import HiringPostsScraper
from src.collectors import get_all as get_types


PENDING = Path(PENDING_QUEUE_FILE)


def main():
    print("=" * 60)
    print(f"  HIRING SCRAPE (HOLD MODE) - {datetime.now()}")
    print("=" * 60)

    types = get_types()
    seen = SeenSet()
    for t in types:
        for key in t.load_seen():
            seen.add(t.name, key)
    print("Seen: " + ", ".join(f"{t.name}={seen.count(t.name)}" for t in types))

    apify = ApifyClient(APIFY_TOKEN)
    result = HiringPostsScraper(apify).run(seen)

    # Persist new items to data files so the dedup set stays consistent and
    # tomorrow's normal scrape doesn't re-fetch the same posts.
    for t in types:
        new = result.get(t.name)
        if not new:
            continue
        stored = load_json(t.storage_file)
        stored.extend(new)
        save_json(t.storage_file, stored)

    # Hold queue-bound items in a pending file instead of publishing now.
    pending = json.loads(PENDING.read_text()) if PENDING.exists() else {}
    held = 0
    for t in types:
        new = result.get(t.name)
        if not new or not t.queue_name:
            continue
        pending.setdefault(t.name, []).extend(new)
        held += len(new)
    PENDING.parent.mkdir(parents=True, exist_ok=True)
    PENDING.write_text(json.dumps(pending, indent=2, default=str))

    print("\n" + "=" * 60)
    print("  HOLD SUMMARY (NOT queued)")
    print("=" * 60)
    for t in types:
        print(f"  {t.name:15s} {result.count(t.name)}")
    print("=" * 60)
    print(f"  Held {held} queueable items in {PENDING}")
    print(f"  Run `python3 scripts/drain_pending.py` later to publish.")


if __name__ == "__main__":
    main()
