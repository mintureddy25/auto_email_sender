from src.collectors import register
from src.collectors.base import DataType
from src.config import PHONE_NUMBERS_FILE


@register
class Phones(DataType):
    name = "phones"
    storage_file = PHONE_NUMBERS_FILE
    dedup_key = "phone"
    # No queue — store-only for now. Add queue_name later if a phone sender exists.
