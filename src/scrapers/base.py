"""Base classes for scrapers.

Scrapers return a ScrapeResult keyed by data-type name (e.g. "emails",
"phones") so new types can be added without touching this file.

Adding a new scraper:
  1. Create src/scrapers/<your_name>.py
  2. Subclass BaseScraper, decorate with @register, implement run()
  3. Append items via result.add(type_name, item)
     and dedup via seen.has(type_name, key) / seen.add(type_name, key)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class ScrapeResult:
    items: Dict[str, List[dict]] = field(default_factory=dict)

    def add(self, type_name: str, item: dict) -> None:
        self.items.setdefault(type_name, []).append(item)

    def extend(self, type_name: str, items: List[dict]) -> None:
        self.items.setdefault(type_name, []).extend(items)

    def get(self, type_name: str) -> List[dict]:
        return self.items.get(type_name, [])

    def count(self, type_name: str) -> int:
        return len(self.items.get(type_name, []))

    def merge(self, other: "ScrapeResult") -> None:
        for k, v in other.items.items():
            self.items.setdefault(k, []).extend(v)


@dataclass
class SeenSet:
    sets: Dict[str, Set[str]] = field(default_factory=dict)

    def has(self, type_name: str, key: str) -> bool:
        return key in self.sets.get(type_name, set())

    def add(self, type_name: str, key: str) -> None:
        self.sets.setdefault(type_name, set()).add(key)

    def count(self, type_name: str) -> int:
        return len(self.sets.get(type_name, set()))


class BaseScraper:
    name: str = ""

    def __init__(self, apify):
        self.apify = apify

    def collect(self, run) -> list:
        items = []
        if run:
            for item in self.apify.dataset(run["defaultDatasetId"]).iterate_items():
                items.append(item)
        return items

    def run(self, seen: SeenSet) -> ScrapeResult:
        raise NotImplementedError
