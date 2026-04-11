from datetime import datetime

from src.config import SENT_LOG_FILE
from src.utils.file_utils import load_json, save_json


def log_sent(email_data, status):
    sent_log = load_json(SENT_LOG_FILE)
    sent_log.append({
        "email": email_data.get("email"),
        "name": email_data.get("name", ""),
        "company": email_data.get("company", ""),
        "title": email_data.get("title", ""),
        "source": email_data.get("source", ""),
        "subject": email_data.get("subject", ""),
        "status": status,
        "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    save_json(SENT_LOG_FILE, sent_log)
