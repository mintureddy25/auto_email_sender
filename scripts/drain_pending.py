"""
Publish previously-held items from `data/pending_queue.json` into their
RabbitMQ queues, then delete the file.

Pairs with scrape_hold.py — run this when you want the worker to start
processing what was held (e.g. Monday morning).

Usage:
    python3 scripts/drain_pending.py
"""

import _bootstrap  # noqa: F401

import json
from pathlib import Path

from src.config import PENDING_QUEUE_FILE
from src.queue.rabbitmq import publish_batch
from src.collectors import get_all as get_types


PENDING = Path(PENDING_QUEUE_FILE)


def main():
    if not PENDING.exists():
        print(f"No pending file at {PENDING} — nothing to drain.")
        return

    pending = json.loads(PENDING.read_text())
    if not pending:
        print("Pending file is empty — nothing to drain.")
        PENDING.unlink()
        return

    types = {t.name: t for t in get_types()}
    total = 0
    for type_name, items in pending.items():
        t = types.get(type_name)
        if not t:
            print(f"  [skip] unknown type '{type_name}' ({len(items)} items)")
            continue
        if not t.queue_name:
            print(f"  [skip] '{type_name}' has no queue_name ({len(items)} items)")
            continue
        if not items:
            continue
        publish_batch(t, items)
        total += len(items)

    PENDING.unlink()
    print(f"\nDrained {total} items, removed {PENDING}.")


if __name__ == "__main__":
    main()
