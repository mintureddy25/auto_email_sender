from datetime import datetime
from src.config import RECRUITER_TITLES, LOCATIONS, MAX_PEOPLE_EMAILS
from src.utils.extractors import extract_email_from_profile, extract_phone_from_profile, extract_profile_info


def scrape(apify, collect_items, seen_emails, seen_phones):
    print("\n[SOURCE 2] LinkedIn People Search (Recruiters/HR)")
    emails, phones = [], []

    try:
        run = apify.actor("harvestapi/linkedin-profile-search").call(
            run_input={
                "query": "recruiter hiring software engineer developer",
                "currentJobTitles": RECRUITER_TITLES,
                "locations": LOCATIONS,
                "profileScraperMode": "Full + email search",
                "takePages": 5,
                "maxItems": 400,
            }
        )
        items = collect_items(run)
        print(f"  Scraped {len(items)} profiles")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for item in items:
            info = extract_profile_info(item)

            # Email
            if len(emails) < MAX_PEOPLE_EMAILS:
                email = extract_email_from_profile(item)
                if email and email not in seen_emails:
                    emails.append({**info, "email": email, "source": "people_search"})
                    seen_emails.add(email)

            # Phone
            phone = extract_phone_from_profile(item)
            if phone and phone not in seen_phones:
                phones.append({
                    **info, "phone": phone, "source": "people_search",
                    "collected_at": now,
                })
                seen_phones.add(phone)

        print(f"  Got {len(emails)} emails, {len(phones)} phones")

    except Exception as e:
        print(f"  Error: {e}")

    return emails, phones
