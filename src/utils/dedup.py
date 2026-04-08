from src.utils.file_utils import load_json
from src.config import EMAILS_FILE, SENT_LOG_FILE, PHONE_NUMBERS_FILE, FORM_LINKS_FILE, JOB_LINKS_FILE


def get_seen_emails():
    sent_log = load_json(SENT_LOG_FILE)
    all_emails = load_json(EMAILS_FILE)
    seen = set()
    for e in sent_log:
        if e.get("email"):
            seen.add(e["email"])
    for e in all_emails:
        if e.get("email"):
            seen.add(e["email"])
    return seen


def get_seen_phones():
    phones = load_json(PHONE_NUMBERS_FILE)
    return set(p.get("phone", "") for p in phones)


def get_seen_form_links():
    forms = load_json(FORM_LINKS_FILE)
    return set(f.get("link", "") for f in forms)


def get_seen_job_links():
    jobs = load_json(JOB_LINKS_FILE)
    return set(j.get("link", "") for j in jobs)
