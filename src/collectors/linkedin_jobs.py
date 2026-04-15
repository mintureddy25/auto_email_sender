from src.collectors import register
from src.collectors.base import DataType
from src.config import LINKEDIN_JOBS_FILE


@register
class LinkedInJobs(DataType):
    name = "linkedin_jobs"
    storage_file = LINKEDIN_JOBS_FILE
    dedup_key = "link"
