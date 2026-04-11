"""Data type registry with auto-discovery.

A DataType describes something scrapers can collect (emails, phones, ...)
and where it should be stored + queued. Drop a new file in this folder
to register a new type.
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
        importlib.import_module(f"src.collectors.{name}")


def get_all():
    _discover()
    return sorted(_REGISTRY, key=lambda c: c.name)


def get(name: str):
    for c in get_all():
        if c.name == name:
            return c
    return None
