"""
Cron job: Scrapes LinkedIn for emails, phones, form links, job links.
Inserts new contacts into RabbitMQ queues.
"""

from datetime import datetime
from apify_client import ApifyClient

from src.config import APIFY_TOKEN, EMAILS_FILE, PHONE_NUMBERS_FILE, FORM_LINKS_FILE, JOB_LINKS_FILE
from src.utils.file_utils import load_json, save_json
from src.utils.dedup import get_seen_emails, get_seen_phones, get_seen_form_links, get_seen_job_links
from src.queue.rabbitmq import queue_emails
from src.scrapers import hiring_posts, people_search, company_employees

apify = ApifyClient(APIFY_TOKEN)


def collect_items(run):
    items = []
    if run:
        for item in apify.dataset(run["defaultDatasetId"]).iterate_items():
            items.append(item)
    return items


def main():
    print("=" * 60)
    print(f"  AUTO SCRAPER - {datetime.now()}")
    print("=" * 60)

    seen_emails = get_seen_emails()
    seen_phones = get_seen_phones()
    seen_forms = get_seen_form_links()
    seen_jobs = get_seen_job_links()
    print(f"Already processed: {len(seen_emails)} emails, {len(seen_phones)} phones")

    # Source 1: Hiring posts
    post_emails, post_phones, post_forms, post_jobs = hiring_posts.scrape(
        apify, collect_items, seen_emails, seen_phones, seen_forms, seen_jobs
    )

    # Source 2: People search
    people_emails, people_phones = people_search.scrape(
        apify, collect_items, seen_emails, seen_phones
    )

    # Source 3: Company employees
    company_emails, company_phones = company_employees.scrape(
        apify, collect_items, seen_emails, seen_phones
    )

    # Save emails
    new_emails = post_emails + people_emails + company_emails
    if new_emails:
        all_stored = load_json(EMAILS_FILE)
        all_stored.extend(new_emails)
        save_json(EMAILS_FILE, all_stored)

    # Save phones
    all_phones = post_phones + people_phones + company_phones
    if all_phones:
        stored = load_json(PHONE_NUMBERS_FILE)
        stored.extend(all_phones)
        save_json(PHONE_NUMBERS_FILE, stored)

    # Save form links
    if post_forms:
        stored = load_json(FORM_LINKS_FILE)
        stored.extend(post_forms)
        save_json(FORM_LINKS_FILE, stored)

    # Save job links
    if post_jobs:
        stored = load_json(JOB_LINKS_FILE)
        stored.extend(post_jobs)
        save_json(JOB_LINKS_FILE, stored)

    # Queue for sending
    print("\n" + "=" * 60)
    if new_emails:
        queue_emails(new_emails)
    else:
        print("  No new emails to queue.")

    if all_phones:
        print(f"  Saved {len(all_phones)} phone numbers to {PHONE_NUMBERS_FILE}")

    # Summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  Emails:      {len(new_emails)}")
    print(f"  Phones:      {len(all_phones)}")
    print(f"  Form links:  {len(post_forms)}")
    print(f"  Job links:   {len(post_jobs)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
