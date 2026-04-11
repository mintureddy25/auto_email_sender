from datetime import datetime

from src.scrapers import register
from src.scrapers.base import BaseScraper, ScrapeResult, SeenSet
from src.config import (
    HIRING_POST_QUERIES, MAX_POST_EMAILS,
    HIRING_MAX_POSTS, HIRING_POSTED_LIMIT, HIRING_SCRAPE_PAGES,
)
from src.utils.extractors import (
    extract_emails, is_valid_email, extract_phone_numbers,
    extract_form_links, extract_job_links, extract_short_links,
)
from src.utils.url_resolver import resolve_map


@register
class HiringPostsScraper(BaseScraper):
    name = "hiring_posts"

    def run(self, seen: SeenSet) -> ScrapeResult:
        print(f"\n[{self.name}] LinkedIn Hiring Posts")
        result = ScrapeResult()

        try:
            run = self.apify.actor("harvestapi/linkedin-post-search").call(
                run_input={
                    "searchQueries": HIRING_POST_QUERIES,
                    "scrapePages": HIRING_SCRAPE_PAGES,
                    "maxPosts": HIRING_MAX_POSTS,
                    "postedLimit": HIRING_POSTED_LIMIT,
                }
            )
            items = self.collect(run)
            print(f"  Scraped {len(items)} posts")
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Batch-resolve all short links across every post (much faster
            # than per-post resolution).
            all_short_links = []
            for item in items:
                full_text = (item.get("content", "") or "") + " " + (item.get("text", "") or "")
                all_short_links.extend(extract_short_links(full_text))

            if all_short_links:
                print(f"  Resolving {len(set(all_short_links))} unique short links...")
            resolved_lookup = resolve_map(all_short_links)

            for item in items:
                content = item.get("content", "") or ""
                text = item.get("text", "") or ""
                full_text = content + " " + text
                post_url = item.get("url", "") or item.get("postUrl", "")
                author = item.get("author", {})
                author_name = author.get("name", "")

                if result.count("emails") < MAX_POST_EMAILS:
                    for email in extract_emails(full_text):
                        if not seen.has("emails", email) and is_valid_email(email):
                            result.add("emails", {
                                "email": email,
                                "name": author_name,
                                "title": author.get("info", ""),
                                "company": "",
                                "profileUrl": author.get("linkedinUrl", ""),
                                "source": "hiring_post",
                            })
                            seen.add("emails", email)

                for phone in extract_phone_numbers(full_text):
                    if not seen.has("phones", phone):
                        result.add("phones", {
                            "phone": phone, "name": author_name,
                            "title": author.get("info", ""), "company": "",
                            "profileUrl": author.get("linkedinUrl", ""),
                            "postUrl": post_url, "source": "hiring_post",
                            "collected_at": now,
                        })
                        seen.add("phones", phone)

                post_short = extract_short_links(full_text)
                resolved_text = " ".join(resolved_lookup.get(s, "") for s in post_short)
                classify_text = full_text + " " + resolved_text

                for link in extract_form_links(classify_text):
                    if not seen.has("form_links", link):
                        result.add("form_links", {
                            "link": link, "author": author_name,
                            "postUrl": post_url, "source": "hiring_post",
                            "collected_at": now,
                        })
                        seen.add("form_links", link)

                for link in extract_job_links(classify_text):
                    if not seen.has("job_links", link):
                        result.add("job_links", {
                            "link": link, "author": author_name,
                            "postUrl": post_url, "source": "hiring_post",
                            "collected_at": now,
                        })
                        seen.add("job_links", link)

            print(f"  Got {result.count('emails')} emails, {result.count('phones')} phones, "
                  f"{result.count('form_links')} forms, {result.count('job_links')} job links")

        except Exception as e:
            print(f"  Error: {e}")

        return result
