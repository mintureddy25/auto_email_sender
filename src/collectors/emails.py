from src.collectors import register
from src.collectors.base import DataType
from src.config import EMAILS_FILE, SENT_LOG_FILE, EMAIL_QUEUE, EMAIL_DLX, EMAIL_FAILED_QUEUE
from src.utils.file_utils import load_json


@register
class Emails(DataType):
    name = "emails"
    storage_file = EMAILS_FILE
    dedup_key = "email"

    queue_name = EMAIL_QUEUE
    dlx_name = EMAIL_DLX
    failed_queue_name = EMAIL_FAILED_QUEUE

    @classmethod
    def load_seen(cls):
        seen = super().load_seen()
        # Also treat previously-sent addresses as seen.
        for entry in load_json(SENT_LOG_FILE):
            addr = entry.get("email")
            if addr:
                seen.add(addr)
        return seen
