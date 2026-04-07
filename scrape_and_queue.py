"""
Cron job: Runs once daily at 9AM.
1. LinkedIn Hiring Posts -> extract emails from post text
2. People Search -> recruiter/HR emails directly
3. Company Employees -> HR emails directly
Inserts NEW emails into Redis queue (skips already sent/queued).
Queue worker (24/7) picks them up and sends instantly.
"""

import json
import os
import re
from datetime import datetime

import redis
from apify_client import ApifyClient
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Apify
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
apify = ApifyClient(APIFY_TOKEN)

# Redis
redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    decode_responses=True,
    username=os.getenv("REDIS_USERNAME"),
    password=os.getenv("REDIS_PASSWORD"),
)

QUEUE_NAME = "auto_email_queue"
EMAILS_FILE = os.path.join(BASE_DIR, "emails.json")
SENT_LOG_FILE = os.path.join(BASE_DIR, "sent_log.json")
SUBJECT = "Full Stack Developer | 3+ Yrs | React, Next.js, Node.js, Java"

# ---------- CONFIG ----------

HIRING_POST_QUERIES = [
    "hiring full stack developer India",
    "hiring software engineer India",
    "hiring backend developer India",
    "hiring frontend developer India",
    "hiring SDE India",
    "hiring react developer India",
    "hiring node.js developer India",
]

RECRUITER_TITLES = [
    "Technical Recruiter",
    "HR Manager",
    "Talent Acquisition",
    "Recruiter",
    "Hiring Manager",
]

LOCATIONS = ["India", "Bangalore", "Hyderabad", "Pune", "Delhi", "Mumbai"]

TARGET_COMPANIES = [
    "https://www.linkedin.com/company/google",
    "https://www.linkedin.com/company/microsoft",
    "https://www.linkedin.com/company/amazon",
    "https://www.linkedin.com/company/meta",
    "https://www.linkedin.com/company/flipkart",
    "https://www.linkedin.com/company/swiggy",
    "https://www.linkedin.com/company/zomato",
    "https://www.linkedin.com/company/razorpay",
    "https://www.linkedin.com/company/phonepe-internet",
    "https://www.linkedin.com/company/paytm",
]

# Target emails per source
MAX_POST_EMAILS = 50
MAX_PEOPLE_EMAILS = 50
MAX_COMPANY_EMAILS = 50

# -------------------------------------------------


def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return []


def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def collect_items(run):
    items = []
    if run:
        for item in apify.dataset(run["defaultDatasetId"]).iterate_items():
            items.append(item)
    return items


def get_already_processed_emails():
    """All emails already sent or in database"""
    sent_log = load_json(SENT_LOG_FILE)
    all_emails = load_json(EMAILS_FILE)
    seen = set()
    for e in sent_log:
        if e.get("email"):
            seen.add(e["email"])
    for e in all_emails:
        if e.get("email"):
            seen.add(e["email"])
    return seen


# ---------- SOURCE 1: LinkedIn Hiring Posts (emails in post text) ----------


def scrape_hiring_posts(already_seen):
    print("\n[SOURCE 1] LinkedIn Hiring Posts (emails from post text)")
    emails = []

    try:
        run = apify.actor("harvestapi/linkedin-post-search").call(
            run_input={
                "searchQueries": HIRING_POST_QUERIES,
                "scrapePages": 3,
                "maxPosts": 50,
            }
        )
        items = collect_items(run)
        print(f"  Scraped {len(items)} posts")

        for item in items:
            if len(emails) >= MAX_POST_EMAILS:
                break

            # Extract emails from post content using regex
            content = item.get("content", "") or ""
            text = item.get("text", "") or ""
            full_text = content + " " + text

            found_emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", full_text)

            author = item.get("author", {})
            author_name = author.get("name", "")

            for email in found_emails:
                # Skip common non-personal emails
                if email in already_seen:
                    continue
                if any(skip in email.lower() for skip in ["noreply", "no-reply", "example.com", "test.com"]):
                    continue

                emails.append({
                    "email": email,
                    "name": author_name,
                    "title": author.get("info", ""),
                    "company": "",
                    "profileUrl": author.get("linkedinUrl", ""),
                    "source": "hiring_post",
                })
                already_seen.add(email)

        print(f"  Got {len(emails)} NEW emails from posts")

    except Exception as e:
        print(f"  Error: {e}")

    return emails


# ---------- SOURCE 2: People Search (recruiters/HR with emails) ----------


def search_recruiters(already_seen):
    print("\n[SOURCE 2] LinkedIn People Search (Recruiters/HR)")
    emails = []

    try:
        run = apify.actor("harvestapi/linkedin-profile-search").call(
            run_input={
                "query": "recruiter hiring software engineer developer",
                "currentJobTitles": RECRUITER_TITLES,
                "locations": LOCATIONS,
                "profileScraperMode": "Full + email search",
                "takePages": 5,
                "maxItems": 200,  # scrape more, filter to 50 new
            }
        )
        items = collect_items(run)
        print(f"  Scraped {len(items)} profiles")

        for item in items:
            if len(emails) >= MAX_PEOPLE_EMAILS:
                break

            # Email can be in 'emails' array or 'email' string
            email = None
            if item.get("emails") and isinstance(item["emails"], list) and len(item["emails"]) > 0:
                email = item["emails"][0].get("email")
            if not email:
                email = item.get("email") or item.get("emailAddress")

            if email and email not in already_seen:
                name = f"{item.get('firstName', '')} {item.get('lastName', '')}".strip()
                if not name:
                    name = item.get("fullName") or item.get("name", "")
                emails.append({
                    "email": email,
                    "name": name,
                    "title": item.get("headline") or item.get("title", ""),
                    "company": item.get("company") or item.get("companyName", ""),
                    "profileUrl": item.get("linkedinUrl") or item.get("profileUrl") or item.get("url", ""),
                    "source": "people_search",
                })
                already_seen.add(email)

        print(f"  Got {len(emails)} NEW emails")

    except Exception as e:
        print(f"  Error: {e}")

    return emails


# ---------- SOURCE 3: Company Employees (HR at target companies) ----------


def scrape_company_recruiters(already_seen):
    print("\n[SOURCE 3] Company Employees (HR/Recruiters)")
    emails = []

    try:
        run = apify.actor("harvestapi/linkedin-company-employees").call(
            run_input={
                "companies": TARGET_COMPANIES,
                "profileScraperMode": "Full + email search ($12 per 1k)",
                "jobTitles": RECRUITER_TITLES,
                "locations": ["India"],
                "maxItems": 200,  # scrape more, filter to 50 new
                "companyBatchMode": "one_by_one",
            }
        )
        items = collect_items(run)
        print(f"  Scraped {len(items)} profiles")

        for item in items:
            if len(emails) >= MAX_COMPANY_EMAILS:
                break

            # Email can be in 'emails' array or 'email' string
            email = None
            if item.get("emails") and isinstance(item["emails"], list) and len(item["emails"]) > 0:
                email = item["emails"][0].get("email")
            if not email:
                email = item.get("email") or item.get("emailAddress")

            if email and email not in already_seen:
                name = f"{item.get('firstName', '')} {item.get('lastName', '')}".strip()
                if not name:
                    name = item.get("fullName") or item.get("name", "")
                emails.append({
                    "email": email,
                    "name": name,
                    "title": item.get("headline") or item.get("title", ""),
                    "company": item.get("company") or item.get("companyName", ""),
                    "profileUrl": item.get("linkedinUrl") or item.get("profileUrl") or item.get("url", ""),
                    "source": "company_employees",
                })
                already_seen.add(email)

        print(f"  Got {len(emails)} NEW emails")

    except Exception as e:
        print(f"  Error: {e}")

    return emails


# ---------- QUEUE: Insert into Redis ----------


def insert_into_queue(new_emails):
    count = 0
    for entry in new_emails:
        job = json.dumps({
            "email": entry["email"],
            "name": entry.get("name", ""),
            "company": entry.get("company", ""),
            "title": entry.get("title", ""),
            "source": entry.get("source", ""),
            "subject": SUBJECT,
        })
        redis_client.rpush(QUEUE_NAME, job)
        count += 1

    print(f"\n  Inserted {count} jobs into Redis queue '{QUEUE_NAME}'")
    print(f"  Queue length: {redis_client.llen(QUEUE_NAME)}")


# ---------- MAIN ----------


def main():
    print("=" * 60)
    print(f"  AUTO SCRAPER - {datetime.now()}")
    print(f"  Sources: Posts + People Search + Company Employees")
    print("=" * 60)

    already_seen = get_already_processed_emails()
    print(f"Already processed: {len(already_seen)} emails")

    # Source 1: Emails from hiring post text
    post_emails = scrape_hiring_posts(already_seen)

    # Source 2: Recruiter emails from people search
    people_emails = search_recruiters(already_seen)

    # Source 3: HR emails from company employees
    company_emails = scrape_company_recruiters(already_seen)

    # Merge and save to emails.json
    all_stored = load_json(EMAILS_FILE)
    new_emails = post_emails + people_emails + company_emails

    for entry in new_emails:
        all_stored.append(entry)
    save_json(EMAILS_FILE, all_stored)

    # Insert into Redis queue
    print("\n" + "=" * 60)
    if new_emails:
        insert_into_queue(new_emails)
    else:
        print("  No new emails to queue.")

    # Summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  Hiring Post emails:   {len(post_emails)}")
    print(f"  People Search emails: {len(people_emails)}")
    print(f"  Company emails:       {len(company_emails)}")
    print(f"  Total NEW queued:     {len(new_emails)}")
    print(f"  Total in database:    {len(all_stored)}")
    print(f"  Worker sends them automatically.")
    print("=" * 60)


if __name__ == "__main__":
    main()
