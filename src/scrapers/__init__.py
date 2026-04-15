"""Scraper registry with auto-discovery.

Every module in this package that defines a @register-decorated class is
auto-imported on get_all() — drop a new file in here and it's live.
"""

import importlib
import pkgutil
from pathlib import Path

_REGISTRY = []


def register(cls):
    _REGISTRY.append(cls)
    return cls


def _discover():
    pkg_dir = Path(__file__).parent
    for mod_info in pkgutil.iter_modules([str(pkg_dir)]):
        name = mod_info.name
        if name.startswith("_") or name == "base":
            continue
        importlib.import_module(f"src.scrapers.{name}")


def get_all():
    from src.config import SCRAPER_ENABLED
    _discover()
    return sorted(
        [c for c in _REGISTRY if SCRAPER_ENABLED.get(c.name, True)],
        key=lambda c: c.name,
    )
