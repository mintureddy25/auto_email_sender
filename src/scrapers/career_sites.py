from datetime import datetime

from src.scrapers import register
from src.scrapers.base import BaseScraper, ScrapeResult, SeenSet
from src.config import (
    CAREER_SITE_DOMAINS, CAREER_SITE_LIMIT, CAREER_SITE_TIME_RANGE,
    CAREER_SITE_EXPERIENCE, JOBS_TITLES, LOCATIONS,
)
from src.utils.extractors import extract_form_links

_FORM_MARKERS = ("forms.gle", "docs.google.com/forms", "forms.office.com",
                 "typeform.com", "jotform.com")


def _is_form_link(url):
    return any(m in url for m in _FORM_MARKERS)


@register
class CareerSitesScraper(BaseScraper):
    name = "career_sites"

    def run(self, seen: SeenSet) -> ScrapeResult:
        print(f"\n[{self.name}] Company Career Pages")
        result = ScrapeResult()

        try:
            run = self.apify.actor("fantastic-jobs/career-site-job-listing-api").call(
                run_input={
                    "timeRange": CAREER_SITE_TIME_RANGE,
                    "limit": CAREER_SITE_LIMIT,
                    "titleSearch": JOBS_TITLES,
                    "locationSearch": LOCATIONS,
                    "domainFilter": CAREER_SITE_DOMAINS,
                    "aiExperienceLevelFilter": CAREER_SITE_EXPERIENCE,
                    "descriptionType": "text",
                    "removeAgency": True,
                }
            )
            items = self.collect(run)
            print(f"  Scraped {len(items)} career listings")
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for item in items:
                job_url = item.get("url", "") or item.get("apply_url", "")
                title = item.get("title", "")
                company = item.get("organization", "") or item.get("company", "")
                location = item.get("locations_derived", "") or item.get("location", "")
                description = item.get("description", "") or ""
                ats = item.get("ats", "")

                if isinstance(location, list):
                    location = ", ".join(location)

                if not job_url:
                    continue

                if _is_form_link(job_url):
                    if not seen.has("form_links", job_url):
                        result.add("form_links", {
                            "link": job_url,
                            "author": company,
                            "title": title,
                            "source": "career_sites",
                            "collected_at": now,
                        })
                        seen.add("form_links", job_url)
                else:
                    if not seen.has("job_links", job_url):
                        result.add("job_links", {
                            "link": job_url,
                            "title": title,
                            "company": company,
                            "location": location,
                            "ats": ats,
                            "source": "career_sites",
                            "collected_at": now,
                        })
                        seen.add("job_links", job_url)

                # Also check description for embedded form links
                for form_url in extract_form_links(description):
                    if not seen.has("form_links", form_url):
                        result.add("form_links", {
                            "link": form_url,
                            "author": company,
                            "title": title,
                            "source": "career_sites",
                            "collected_at": now,
                        })
                        seen.add("form_links", form_url)

            print(f"  Got {result.count('job_links')} job links, "
                  f"{result.count('form_links')} form links")

        except Exception as e:
            print(f"  Error: {e}")

        return result
