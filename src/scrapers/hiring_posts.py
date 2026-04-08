import re
from datetime import datetime
from src.config import HIRING_POST_QUERIES, MAX_POST_EMAILS
from src.utils.extractors import (
    extract_emails, is_valid_email, extract_phone_numbers,
    extract_form_links, extract_job_links,
)


def scrape(apify, collect_items, seen_emails, seen_phones, seen_forms, seen_jobs):
    print("\n[SOURCE 1] LinkedIn Hiring Posts")
    emails, phones, forms, jobs = [], [], [], []

    try:
        run = apify.actor("harvestapi/linkedin-post-search").call(
            run_input={
                "searchQueries": HIRING_POST_QUERIES,
                "scrapePages": 10,
                "maxPosts": 50,
                "postedLimit": "week",
            }
        )
        items = collect_items(run)
        print(f"  Scraped {len(items)} posts")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for item in items:
            content = item.get("content", "") or ""
            text = item.get("text", "") or ""
            full_text = content + " " + text
            post_url = item.get("url", "") or item.get("postUrl", "")
            author = item.get("author", {})
            author_name = author.get("name", "")

            # Emails
            if len(emails) < MAX_POST_EMAILS:
                for email in extract_emails(full_text):
                    if email not in seen_emails and is_valid_email(email):
                        emails.append({
                            "email": email,
                            "name": author_name,
                            "title": author.get("info", ""),
                            "company": "",
                            "profileUrl": author.get("linkedinUrl", ""),
                            "source": "hiring_post",
                        })
                        seen_emails.add(email)

            # Phones
            for phone in extract_phone_numbers(full_text):
                if phone not in seen_phones:
                    phones.append({
                        "phone": phone, "name": author_name,
                        "title": author.get("info", ""), "company": "",
                        "profileUrl": author.get("linkedinUrl", ""),
                        "postUrl": post_url, "source": "hiring_post",
                        "collected_at": now,
                    })
                    seen_phones.add(phone)

            # Forms
            for link in extract_form_links(full_text):
                if link not in seen_forms:
                    forms.append({
                        "link": link, "author": author_name,
                        "postUrl": post_url, "source": "hiring_post",
                        "collected_at": now,
                    })
                    seen_forms.add(link)

            # Job links
            for link in extract_job_links(full_text):
                if link not in seen_jobs:
                    jobs.append({
                        "link": link, "author": author_name,
                        "postUrl": post_url, "source": "hiring_post",
                        "collected_at": now,
                    })
                    seen_jobs.add(link)

        print(f"  Got {len(emails)} emails, {len(phones)} phones, {len(forms)} forms, {len(jobs)} job links")

    except Exception as e:
        print(f"  Error: {e}")

    return emails, phones, forms, jobs
