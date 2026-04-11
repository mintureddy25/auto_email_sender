"""DataType base class.

Each data type owns:
  - a name (used everywhere as the key)
  - a storage file (JSON)
  - a dedup key (which field in each item is unique)
  - an optional queue_name (if the type needs async processing by a sender)

Override load_seen() if dedup needs extra sources beyond storage_file
(e.g. emails also merge from sent_log.json).
"""

from typing import Optional, Set

from src.utils.file_utils import load_json


class DataType:
    name: str = ""
    storage_file: str = ""
    dedup_key: str = ""

    # Queue wiring — leave None for storage-only types (no sender)
    queue_name: Optional[str] = None
    dlx_name: Optional[str] = None
    failed_queue_name: Optional[str] = None

    @classmethod
    def get_dlx(cls) -> Optional[str]:
        if cls.queue_name is None:
            return None
        return cls.dlx_name or f"{cls.queue_name}_dlx"

    @classmethod
    def get_failed_queue(cls) -> Optional[str]:
        if cls.queue_name is None:
            return None
        return cls.failed_queue_name or f"{cls.queue_name}_failed"

    @classmethod
    def load_seen(cls) -> Set[str]:
        items = load_json(cls.storage_file)
        return {i.get(cls.dedup_key, "") for i in items if i.get(cls.dedup_key)}
