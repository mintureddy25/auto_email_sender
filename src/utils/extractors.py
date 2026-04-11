import re

PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}"
)
FORM_LINK_REGEX = re.compile(
    r"https?://(?:docs\.google\.com/forms|forms\.gle|forms\.office\.com|forms\.microsoft\.com)/\S+",
    re.IGNORECASE,
)
JOB_LINK_REGEX = re.compile(
    r"https?://(?:[\w-]+\.)?(?:lever\.co|greenhouse\.io|workday\.com|jobs\.ashbyhq\.com|boards\.greenhouse\.io|apply\.workable\.com|jobs\.smartrecruiters\.com|careers\.[\w-]+\.com|[\w-]+\.applytojob\.com|angel\.co/[\w-]+/jobs|linkedin\.com/jobs)/\S+",
    re.IGNORECASE,
)
SHORT_LINK_REGEX = re.compile(
    r"https?://(?:lnkd\.in|bit\.ly|tinyurl\.com|t\.co|buff\.ly|ow\.ly|rebrand\.ly|cutt\.ly)/\S+",
    re.IGNORECASE,
)
EMAIL_REGEX = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

SKIP_EMAILS = ["noreply", "no-reply", "example.com", "test.com"]


def extract_emails(text):
    return EMAIL_REGEX.findall(text)


def is_valid_email(email):
    return not any(skip in email.lower() for skip in SKIP_EMAILS)


def extract_phone_numbers(text):
    matches = PHONE_REGEX.findall(text)
    phones = []
    for m in matches:
        cleaned = re.sub(r"[^\d+]", "", m)
        if len(cleaned) >= 10:
            phones.append(cleaned)
    return phones


def extract_form_links(text):
    return FORM_LINK_REGEX.findall(text)


def extract_job_links(text):
    return JOB_LINK_REGEX.findall(text)


def extract_short_links(text):
    return SHORT_LINK_REGEX.findall(text)


def extract_email_from_profile(item):
    email = None
    if item.get("emails") and isinstance(item["emails"], list) and len(item["emails"]) > 0:
        email = item["emails"][0].get("email")
    if not email:
        email = item.get("email") or item.get("emailAddress")
    return email


def extract_phone_from_profile(item):
    phone = item.get("phone") or item.get("phoneNumber") or item.get("contactNumber")
    if not phone and item.get("phones") and isinstance(item["phones"], list) and len(item["phones"]) > 0:
        phone = item["phones"][0] if isinstance(item["phones"][0], str) else item["phones"][0].get("number")
    if phone:
        cleaned = re.sub(r"[^\d+]", "", str(phone))
        if len(cleaned) >= 10:
            return cleaned
    return None


def extract_profile_info(item):
    name = f"{item.get('firstName', '')} {item.get('lastName', '')}".strip()
    if not name:
        name = item.get("fullName") or item.get("name", "")
    return {
        "name": name,
        "title": item.get("headline") or item.get("title", ""),
        "company": item.get("company") or item.get("companyName", ""),
        "profileUrl": item.get("linkedinUrl") or item.get("profileUrl") or item.get("url", ""),
    }
