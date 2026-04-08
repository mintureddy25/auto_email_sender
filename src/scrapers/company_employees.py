from datetime import datetime
from src.config import TARGET_COMPANIES, RECRUITER_TITLES, MAX_COMPANY_EMAILS
from src.utils.extractors import extract_email_from_profile, extract_phone_from_profile, extract_profile_info


def scrape(apify, collect_items, seen_emails, seen_phones):
    print("\n[SOURCE 3] Company Employees (HR/Recruiters)")
    emails, phones = [], []

    try:
        run = apify.actor("harvestapi/linkedin-company-employees").call(
            run_input={
                "companies": TARGET_COMPANIES,
                "profileScraperMode": "Full + email search ($12 per 1k)",
                "jobTitles": RECRUITER_TITLES,
                "locations": ["India"],
                "maxItems": 200,
                "companyBatchMode": "one_by_one",
            }
        )
        items = collect_items(run)
        print(f"  Scraped {len(items)} profiles")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for item in items:
            info = extract_profile_info(item)

            # Email
            if len(emails) < MAX_COMPANY_EMAILS:
                email = extract_email_from_profile(item)
                if email and email not in seen_emails:
                    emails.append({**info, "email": email, "source": "company_employees"})
                    seen_emails.add(email)

            # Phone
            phone = extract_phone_from_profile(item)
            if phone and phone not in seen_phones:
                phones.append({
                    **info, "phone": phone, "source": "company_employees",
                    "collected_at": now,
                })
                seen_phones.add(phone)

        print(f"  Got {len(emails)} emails, {len(phones)} phones")

    except Exception as e:
        print(f"  Error: {e}")

    return emails, phones
