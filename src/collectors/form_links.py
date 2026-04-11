from src.collectors import register
from src.collectors.base import DataType
from src.config import FORM_LINKS_FILE


@register
class FormLinks(DataType):
    name = "form_links"
    storage_file = FORM_LINKS_FILE
    dedup_key = "link"
