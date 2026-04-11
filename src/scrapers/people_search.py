from datetime import datetime

from src.scrapers import register
from src.scrapers.base import BaseScraper, ScrapeResult, SeenSet
from src.config import (
    RECRUITER_TITLES, LOCATIONS, MAX_PEOPLE_EMAILS,
    PEOPLE_QUERY, PEOPLE_MAX_ITEMS, PEOPLE_TAKE_PAGES, PEOPLE_SCRAPER_MODE,
)
from src.utils.extractors import (
    extract_email_from_profile, extract_phone_from_profile, extract_profile_info,
)


@register
class PeopleSearchScraper(BaseScraper):
    name = "people_search"

    def run(self, seen: SeenSet) -> ScrapeResult:
        print(f"\n[{self.name}] LinkedIn People Search (Recruiters/HR)")
        result = ScrapeResult()

        try:
            run = self.apify.actor("harvestapi/linkedin-profile-search").call(
                run_input={
                    "query": PEOPLE_QUERY,
                    "currentJobTitles": RECRUITER_TITLES,
                    "locations": LOCATIONS,
                    "profileScraperMode": PEOPLE_SCRAPER_MODE,
                    "takePages": PEOPLE_TAKE_PAGES,
                    "maxItems": PEOPLE_MAX_ITEMS,
                }
            )
            items = self.collect(run)
            print(f"  Scraped {len(items)} profiles")
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for item in items:
                info = extract_profile_info(item)

                if result.count("emails") < MAX_PEOPLE_EMAILS:
                    email = extract_email_from_profile(item)
                    if email and not seen.has("emails", email):
                        result.add("emails", {**info, "email": email, "source": "people_search"})
                        seen.add("emails", email)

                phone = extract_phone_from_profile(item)
                if phone and not seen.has("phones", phone):
                    result.add("phones", {
                        **info, "phone": phone, "source": "people_search",
                        "collected_at": now,
                    })
                    seen.add("phones", phone)

            print(f"  Got {result.count('emails')} emails, {result.count('phones')} phones")

        except Exception as e:
            print(f"  Error: {e}")

        return result
