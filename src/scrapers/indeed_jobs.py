from datetime import datetime

from jobspy import scrape_jobs

from src.scrapers import register
from src.scrapers.base import BaseScraper, ScrapeResult, SeenSet
from src.config import (
    JOBSPY_SEARCH_TERMS, JOBSPY_LOCATIONS, JOBSPY_RESULTS_PER_QUERY,
    JOBSPY_HOURS_OLD,
)
from src.utils.extractors import (
    extract_emails, is_valid_email, extract_phone_numbers,
)


@register
class IndeedJobsScraper(BaseScraper):
    name = "indeed_jobs"

    def run(self, seen: SeenSet) -> ScrapeResult:
        print(f"\n[{self.name}] Indeed Jobs (JobSpy)")
        result = ScrapeResult()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_jobs = 0

        for term in JOBSPY_SEARCH_TERMS:
            for location in JOBSPY_LOCATIONS:
                try:
                    df = scrape_jobs(
                        site_name=["indeed", "google"],
                        search_term=term,
                        google_search_term=f"{term} jobs near {location} since last 24 hours",
                        location=location,
                        results_wanted=JOBSPY_RESULTS_PER_QUERY,
                        hours_old=JOBSPY_HOURS_OLD,
                        country_indeed="india",
                    )
                    if df is None or df.empty:
                        continue
                    total_jobs += len(df)
                    for _, row in df.iterrows():
                        job_url = str(row.get("job_url") or "")
                        title = str(row.get("title") or "")
                        company = str(row.get("company") or "")
                        loc = str(row.get("location") or location)
                        description = str(row.get("description") or "")
                        site = str(row.get("site") or "indeed")

                        if job_url and not seen.has("job_links", job_url):
                            result.add("job_links", {
                                "link": job_url,
                                "title": title,
                                "company": company,
                                "location": loc,
                                "source": f"{site}_jobs",
                                "collected_at": now,
                            })
                            seen.add("job_links", job_url)

                        for email in extract_emails(description):
                            if is_valid_email(email) and not seen.has("emails", email):
                                result.add("emails", {
                                    "email": email,
                                    "name": "",
                                    "title": title,
                                    "company": company,
                                    "profileUrl": job_url,
                                    "source": f"{site}_jobs",
                                    "role": title,
                                })
                                seen.add("emails", email)

                        for phone in extract_phone_numbers(description):
                            if not seen.has("phones", phone):
                                result.add("phones", {
                                    "phone": phone, "name": "",
                                    "title": title, "company": company,
                                    "profileUrl": job_url,
                                    "postUrl": job_url, "source": f"{site}_jobs",
                                    "collected_at": now,
                                })
                                seen.add("phones", phone)
                except Exception as e:
                    print(f"  [{term} | {location}] error: {e}")

        print(f"  Scraped {total_jobs} listings; "
              f"got {result.count('job_links')} job links, "
              f"{result.count('emails')} emails, {result.count('phones')} phones")
        return result
