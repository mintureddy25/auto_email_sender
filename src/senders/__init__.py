"""Sender registry with auto-discovery.

Each registered sender consumes from its own queue_name and implements
send(job). Drop a new file in this folder to add a new sender.
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
        importlib.import_module(f"src.senders.{name}")


def get_all():
    _discover()
    return sorted(_REGISTRY, key=lambda c: c.name)
