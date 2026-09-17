"""
One-off recovery: pull cached hiring_posts datasets from Apify (free reads,
no credits spent), run the same extraction as src/scrapers/hiring_posts.py,
and persist + publish like scrape.py does.

Usage:
    python3 scripts/recover_hiring.py [hours_back]   # default 12
"""

import _bootstrap  # noqa: F401

import sys
from datetime import datetime, timedelta, timezone

from apify_client import ApifyClient

from src.config import APIFY_TOKEN
from src.utils.file_utils import load_json, save_json
from src.queue.rabbitmq import publish_batch
from src.scrapers.base import ScrapeResult, SeenSet
from src.scrapers.hiring_posts import _detect_role
from src.collectors import get_all as get_types
from src.utils.extractors import (
    extract_emails, is_valid_email, extract_phone_numbers,
    extract_form_links, extract_job_links, extract_short_links,
)
from src.utils.url_resolver import resolve_map


ACTOR = "harvestapi/linkedin-post-search"


def main():
    hours_back = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    print(f"Recovering {ACTOR} runs since {cutoff.isoformat()}")

    types = get_types()
    seen = SeenSet()
    for t in types:
        for key in t.load_seen():
            seen.add(t.name, key)
    print("Seen: " + ", ".join(f"{t.name}={seen.count(t.name)}" for t in types))

    apify = ApifyClient(APIFY_TOKEN)
    runs = apify.actor(ACTOR).runs().list(limit=20, desc=True).items
    selected = [r for r in runs if r["status"] == "SUCCEEDED" and r["startedAt"] >= cutoff]
    print(f"Found {len(selected)} runs in window")

    items = []
    for r in selected:
        ds = r.get("defaultDatasetId")
        if not ds:
            continue
        batch = list(apify.dataset(ds).iterate_items())
        print(f"  {r['id']} ({r['startedAt']}) -> {len(batch)} posts")
        items.extend(batch)
    print(f"Total posts: {len(items)}")
    if not items:
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = ScrapeResult()

    all_short = []
    for item in items:
        full = (item.get("content", "") or "") + " " + (item.get("text", "") or "")
        all_short.extend(extract_short_links(full))
    if all_short:
        print(f"Resolving {len(set(all_short))} unique short links...")
    resolved = resolve_map(all_short)

    for item in items:
        content = item.get("content", "") or ""
        text = item.get("text", "") or ""
        full = content + " " + text
        post_url = item.get("url", "") or item.get("postUrl", "")
        author = item.get("author", {}) or {}
        author_name = author.get("name", "")
        role = _detect_role(full)

        for email in extract_emails(full):
            if not seen.has("emails", email) and is_valid_email(email):
                result.add("emails", {
                    "email": email, "name": author_name,
                    "title": author.get("info", ""), "company": "",
                    "profileUrl": author.get("linkedinUrl", ""),
                    "source": "hiring_post", "role": role,
                })
                seen.add("emails", email)

        for phone in extract_phone_numbers(full):
            if not seen.has("phones", phone):
                result.add("phones", {
                    "phone": phone, "name": author_name,
                    "title": author.get("info", ""), "company": "",
                    "profileUrl": author.get("linkedinUrl", ""),
                    "postUrl": post_url, "source": "hiring_post",
                    "collected_at": now,
                })
                seen.add("phones", phone)

        post_short = extract_short_links(full)
        resolved_text = " ".join(resolved.get(s, "") for s in post_short)
        classify = full + " " + resolved_text

        for link in extract_form_links(classify):
            if not seen.has("form_links", link):
                result.add("form_links", {
                    "link": link, "author": author_name,
                    "postUrl": post_url, "source": "hiring_post",
                    "collected_at": now,
                })
                seen.add("form_links", link)

        for link in extract_job_links(classify):
            if not seen.has("job_links", link):
                result.add("job_links", {
                    "link": link, "author": author_name,
                    "postUrl": post_url, "source": "hiring_post",
                    "collected_at": now,
                })
                seen.add("job_links", link)

    for t in types:
        new = result.get(t.name)
        if not new:
            continue
        stored = load_json(t.storage_file)
        stored.extend(new)
        save_json(t.storage_file, stored)

    print("\n" + "=" * 60)
    for t in types:
        new = result.get(t.name)
        if new and t.queue_name:
            publish_batch(t, new)

    print("\n" + "=" * 60)
    print("  RECOVERY SUMMARY")
    print("=" * 60)
    for t in types:
        print(f"  {t.name:15s} {result.count(t.name)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
