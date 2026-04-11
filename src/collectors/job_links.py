from src.collectors import register
from src.collectors.base import DataType
from src.config import JOB_LINKS_FILE


@register
class JobLinks(DataType):
    name = "job_links"
    storage_file = JOB_LINKS_FILE
    dedup_key = "link"
