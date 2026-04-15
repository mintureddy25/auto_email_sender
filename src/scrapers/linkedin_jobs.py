import re
from datetime import datetime

from src.scrapers import register
from src.scrapers.base import BaseScraper, ScrapeResult, SeenSet
from src.config import (
    LOCATIONS, JOBS_TITLES, JOBS_POSTED_LIMIT, JOBS_MAX_ITEMS, JOBS_SORT_BY,
    JOBS_EXPERIENCE_LEVELS, JOBS_MAX_EXPERIENCE_YEARS,
)
from src.utils.extractors import extract_form_links

_CAREER_DOMAINS = (
    "greenhouse.io", "lever.co", "ashbyhq.com", "smartrecruiters.com",
    "workday.com", "myworkdayjobs.com", "recruitee.com", "workable.com",
    "bamboohr.com", "breezy.hr", "freshteam.com", "recruiterbox.com",
    "icims.com", "taleo.net", "jobvite.com", "applytojob.com",
)

_EXP_PATTERN = re.compile(
    r'(\d+)\s*(?:\+\s*)?(?:to|-)\s*(\d+)\s*(?:years?|yrs?)',
    re.IGNORECASE,
)
_EXP_MIN_PATTERN = re.compile(
    r'(\d+)\s*\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)',
    re.IGNORECASE,
)


def _is_career_portal(url):
    return any(d in url for d in _CAREER_DOMAINS)


def _is_form_link(url):
    return any(k in url for k in (
        "forms.gle", "docs.google.com/forms", "forms.office.com",
        "typeform.com", "jotform.com",
    ))


def _experience_ok(item, description):
    """Return True if the job requires <= JOBS_MAX_EXPERIENCE_YEARS."""
    exp_level = item.get("experienceLevel")
    if exp_level and exp_level in ("director", "executive", "mid_senior_level"):
        return False

    m = _EXP_PATTERN.search(description)
    if m:
        min_yrs = int(m.group(1))
        return min_yrs < JOBS_MAX_EXPERIENCE_YEARS

    m = _EXP_MIN_PATTERN.search(description)
    if m:
        yrs = int(m.group(1))
        return yrs < JOBS_MAX_EXPERIENCE_YEARS

    return True


@register
class LinkedInJobsScraper(BaseScraper):
    name = "linkedin_jobs"

    def run(self, seen: SeenSet) -> ScrapeResult:
        print(f"\n[{self.name}] LinkedIn Job Listings")
        result = ScrapeResult()

        try:
            run = self.apify.actor("harvestapi/linkedin-job-search").call(
                run_input={
                    "jobTitles": JOBS_TITLES,
                    "locations": LOCATIONS,
                    "maxItems": JOBS_MAX_ITEMS,
                    "postedLimit": JOBS_POSTED_LIMIT,
                    "sortBy": JOBS_SORT_BY,
                    "experienceLevel": JOBS_EXPERIENCE_LEVELS,
                }
            )
            items = self.collect(run)
            print(f"  Scraped {len(items)} job listings")
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            skipped_exp = 0
            for item in items:
                job_url = item.get("linkedinUrl", "")
                company_obj = item.get("company") or {}
                company_name = company_obj.get("name", "") or company_obj.get("universalName", "")
                title = item.get("title", "")
                location_obj = item.get("location") or {}
                location = location_obj.get("linkedinText", "") if isinstance(location_obj, dict) else str(location_obj)
                description = item.get("descriptionText", "") or ""
                apply_method = item.get("applyMethod") or {}
                company_apply = apply_method.get("companyApplyUrl", "")

                if not _experience_ok(item, description):
                    skipped_exp += 1
                    continue

                # Route company apply URL by type
                if company_apply:
                    if _is_form_link(company_apply):
                        if not seen.has("form_links", company_apply):
                            result.add("form_links", {
                                "link": company_apply,
                                "author": company_name,
                                "title": title,
                                "source": "linkedin_jobs",
                                "collected_at": now,
                            })
                            seen.add("form_links", company_apply)
                    elif _is_career_portal(company_apply):
                        if not seen.has("job_links", company_apply):
                            result.add("job_links", {
                                "link": company_apply,
                                "linkedinUrl": job_url,
                                "title": title,
                                "company": company_name,
                                "location": location,
                                "source": "linkedin_jobs",
                                "collected_at": now,
                            })
                            seen.add("job_links", company_apply)
                    else:
                        if not seen.has("job_links", company_apply):
                            result.add("job_links", {
                                "link": company_apply,
                                "linkedinUrl": job_url,
                                "title": title,
                                "company": company_name,
                                "location": location,
                                "source": "linkedin_jobs",
                                "collected_at": now,
                            })
                            seen.add("job_links", company_apply)

                # Always store LinkedIn job URL separately
                if job_url and not seen.has("linkedin_jobs", job_url):
                    result.add("linkedin_jobs", {
                        "link": job_url,
                        "title": title,
                        "company": company_name,
                        "location": location,
                        "experienceLevel": item.get("experienceLevel"),
                        "employmentType": item.get("employmentType"),
                        "applicants": item.get("applicants"),
                        "postedDate": item.get("postedDate"),
                        "source": "linkedin_jobs",
                        "collected_at": now,
                    })
                    seen.add("linkedin_jobs", job_url)

                # Check description for form links
                for form_url in extract_form_links(description):
                    if not seen.has("form_links", form_url):
                        result.add("form_links", {
                            "link": form_url,
                            "author": company_name,
                            "title": title,
                            "source": "linkedin_jobs",
                            "collected_at": now,
                        })
                        seen.add("form_links", form_url)

            print(f"  Got {result.count('linkedin_jobs')} linkedin jobs, "
                  f"{result.count('job_links')} career portal links, "
                  f"{result.count('form_links')} form links "
                  f"(skipped {skipped_exp} for exp > {JOBS_MAX_EXPERIENCE_YEARS}yr)")

        except Exception as e:
            print(f"  Error: {e}")

        return result
