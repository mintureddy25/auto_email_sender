from datetime import datetime

from src.scrapers import register
from src.scrapers.base import BaseScraper, ScrapeResult, SeenSet
from src.config import (
    TARGET_COMPANIES, RECRUITER_TITLES, MAX_COMPANY_EMAILS, LOCATIONS,
    COMPANY_MAX_ITEMS, COMPANY_SCRAPER_MODE, COMPANY_BATCH_MODE,
)
from src.utils.extractors import (
    extract_email_from_profile, extract_phone_from_profile, extract_profile_info,
)


@register
class CompanyEmployeesScraper(BaseScraper):
    name = "company_employees"

    def run(self, seen: SeenSet) -> ScrapeResult:
        print(f"\n[{self.name}] Company Employees (HR/Recruiters)")
        result = ScrapeResult()

        try:
            run = self.apify.actor("harvestapi/linkedin-company-employees").call(
                run_input={
                    "companies": TARGET_COMPANIES,
                    "profileScraperMode": COMPANY_SCRAPER_MODE,
                    "jobTitles": RECRUITER_TITLES,
                    "locations": LOCATIONS,
                    "maxItems": COMPANY_MAX_ITEMS,
                    "companyBatchMode": COMPANY_BATCH_MODE,
                }
            )
            items = self.collect(run)
            print(f"  Scraped {len(items)} profiles")
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for item in items:
                info = extract_profile_info(item)

                if result.count("emails") < MAX_COMPANY_EMAILS:
                    email = extract_email_from_profile(item)
                    if email and not seen.has("emails", email):
                        result.add("emails", {**info, "email": email, "source": "company_employees"})
                        seen.add("emails", email)

                phone = extract_phone_from_profile(item)
                if phone and not seen.has("phones", phone):
                    result.add("phones", {
                        **info, "phone": phone, "source": "company_employees",
                        "collected_at": now,
                    })
                    seen.add("phones", phone)

            print(f"  Got {result.count('emails')} emails, {result.count('phones')} phones")

        except Exception as e:
            print(f"  Error: {e}")

        return result
