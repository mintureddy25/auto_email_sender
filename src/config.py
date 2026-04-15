import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Apify
APIFY_TOKEN = os.getenv("APIFY_TOKEN")

# RabbitMQ
RABBITMQ_URL = os.getenv("RABBITMQ_URL")

# Per-data-type queue names (each type owns its own queue + DLX + failed queue).
# Add a new block here when you register a new DataType with a queue_name.
EMAIL_QUEUE = "auto_email_queue"
EMAIL_DLX = "auto_email_dlx"
EMAIL_FAILED_QUEUE = "auto_email_failed"

# Email
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", 587))
SUBJECT = "Full Stack Developer | 3+ Yrs Experience"

SUBJECT_BY_SOURCE = {
    "hiring_post": "Re: Your {role} hiring post — 3+ Yrs Experience",
    "people_search": "Full Stack Developer | Open to Opportunities",
    "company_employees": "Full Stack Developer interested in {company}",
}

# Data files
DATA_DIR = os.path.join(BASE_DIR, "data")
EMAILS_FILE = os.path.join(DATA_DIR, "emails.json")
SENT_LOG_FILE = os.path.join(DATA_DIR, "sent_log.json")
PHONE_NUMBERS_FILE = os.path.join(DATA_DIR, "phone_numbers.json")
FORM_LINKS_FILE = os.path.join(DATA_DIR, "form_links.json")
JOB_LINKS_FILE = os.path.join(DATA_DIR, "job_links.json")
LINKEDIN_JOBS_FILE = os.path.join(DATA_DIR, "linkedin_jobs.json")
RESEND_EMAILS_FILE = os.path.join(DATA_DIR, "resend_emails.json")
RESUME_PDF = os.path.join(BASE_DIR, "saitejareddyresume.pdf")

# Scraper enable/disable — set False to skip a scraper without deleting the file
SCRAPER_ENABLED = {
    "hiring_posts": True,
    "people_search": True,
    "company_employees": True,
    "linkedin_jobs": False,
    "career_sites": False,
}

# Scraper config
HIRING_POST_QUERIES = [
    # Pune
    "hiring full stack developer Pune",
    "hiring software engineer Pune",
    "hiring SDE Pune",
    # Hyderabad
    "hiring full stack developer Hyderabad",
    "hiring software engineer Hyderabad",
    "hiring SDE Hyderabad",
]

RECRUITER_TITLES = [
    "Technical Recruiter",
    "HR Manager",
    "Talent Acquisition",
    "Recruiter",
    "Hiring Manager",
]

LOCATIONS = ["Pune", "Hyderabad"]

TARGET_COMPANIES = [
    # Pune-heavy product / SaaS
    "https://www.linkedin.com/company/icertis",
    "https://www.linkedin.com/company/druva",
    "https://www.linkedin.com/company/persistent-systems",
    "https://www.linkedin.com/company/bmc-software",
    "https://www.linkedin.com/company/veritas",
    "https://www.linkedin.com/company/vmware",
    "https://www.linkedin.com/company/nvidia",
    "https://www.linkedin.com/company/mastercard",
    "https://www.linkedin.com/company/barclays",
    "https://www.linkedin.com/company/credit-suisse",
    "https://www.linkedin.com/company/zs-associates",
    "https://www.linkedin.com/company/gslab",
    "https://www.linkedin.com/company/cybage-software",
    "https://www.linkedin.com/company/kpit",
    "https://www.linkedin.com/company/tieto",
    "https://www.linkedin.com/company/harbinger-systems",
    "https://www.linkedin.com/company/thoughtworks",
    "https://www.linkedin.com/company/payatu",
    # Hyderabad-heavy product / engineering
    "https://www.linkedin.com/company/microsoft",
    "https://www.linkedin.com/company/google",
    "https://www.linkedin.com/company/amazon",
    "https://www.linkedin.com/company/apple",
    "https://www.linkedin.com/company/facebook",
    "https://www.linkedin.com/company/uber",
    "https://www.linkedin.com/company/salesforce",
    "https://www.linkedin.com/company/servicenow",
    "https://www.linkedin.com/company/qualcomm",
    "https://www.linkedin.com/company/darwinbox",
    "https://www.linkedin.com/company/skitai",
    "https://www.linkedin.com/company/pharmeasymarg",
    "https://www.linkedin.com/company/highradius-corporation",
    "https://www.linkedin.com/company/skyhighsecurity",
    "https://www.linkedin.com/company/factset",
    "https://www.linkedin.com/company/broadcomcorporation",
    # Both Pune + Hyderabad offices
    "https://www.linkedin.com/company/adobe",
    "https://www.linkedin.com/company/oracle",
    "https://www.linkedin.com/company/ibm",
    "https://www.linkedin.com/company/sap",
    "https://www.linkedin.com/company/accenture",
    "https://www.linkedin.com/company/tcs",
    "https://www.linkedin.com/company/infosys",
    "https://www.linkedin.com/company/wipro",
    "https://www.linkedin.com/company/cognizant",
    "https://www.linkedin.com/company/capgemini",
    # Indian product / fintech with Pune + Hyd hiring
    "https://www.linkedin.com/company/swiggy",
    "https://www.linkedin.com/company/zomato",
    "https://www.linkedin.com/company/razorpay",
    "https://www.linkedin.com/company/phonepe-internet",
    "https://www.linkedin.com/company/paytm",
    "https://www.linkedin.com/company/meesho",
    "https://www.linkedin.com/company/dream11",
    "https://www.linkedin.com/company/freshworks",
    "https://www.linkedin.com/company/zoho",
    "https://www.linkedin.com/company/postman",
]

MAX_POST_EMAILS = 50
MAX_PEOPLE_EMAILS = 50
MAX_COMPANY_EMAILS = 50

# --- Per-scraper Apify filters (all tunables live here) ---
# hiring_posts
HIRING_MAX_POSTS = 60
HIRING_POSTED_LIMIT = "24h"
HIRING_SCRAPE_PAGES = 10

# people_search
PEOPLE_QUERY = "recruiter hiring software engineer developer"
PEOPLE_MAX_ITEMS = 400
PEOPLE_TAKE_PAGES = 5
PEOPLE_SCRAPER_MODE = "Full + email search"

# company_employees
COMPANY_MAX_ITEMS = 200
COMPANY_SCRAPER_MODE = "Full + email search ($12 per 1k)"
COMPANY_BATCH_MODE = "one_by_one"

# linkedin_jobs (harvestapi/linkedin-job-search)
JOBS_TITLES = [
    "Full Stack Developer",
    "Software Engineer",
    "SDE",
    "Frontend Developer",
    "Backend Developer",
]
JOBS_POSTED_LIMIT = "24h"
JOBS_MAX_ITEMS = 50
JOBS_SORT_BY = "date"
JOBS_EXPERIENCE_LEVELS = ["entry_level", "associate", "mid_senior_level"]
JOBS_MAX_EXPERIENCE_YEARS = 5

# career_sites (fantastic-jobs/career-site-job-listing-api)
CAREER_SITE_DOMAINS = [
    # Big tech India
    "uber.com",
    "microsoft.com",
    "google.com",
    "amazon.jobs",
    "atlassian.com",
    "intuit.com",
    "adobe.com",
    "salesforce.com",
    "oracle.com",
    "ibm.com",
    "paypal.com",
    "visa.com",
    # Indian unicorns
    "swiggy.com",
    "zomato.com",
    "flipkart.com",
    "meesho.com",
    "olacabs.com",
    "paytm.com",
    "phonepe.com",
    "dream11.com",
    "pinelabs.com",
    "byjus.com",
    "upgrad.com",
    # Mid-stage SaaS
    "postman.com",
    "browserstack.com",
    "freshworks.com",
    "zoho.com",
    "innovaccer.com",
    "druva.com",
    "chargebee.com",
    "icertis.com",
    # AI / Dev tools
    "sarvam.ai",
    "composio.dev",
    "atlan.com",
    "hasura.io",
    "clevertap.com",
    "moengage.com",
    "rocketlane.com",
    "last9.io",
    "appsmith.com",
    # Fintech / Quick commerce
    "razorpay.com",
    "cred.club",
    "groww.in",
    "zeptonow.com",
    "blinkit.com",
]
CAREER_SITE_LIMIT = 200
CAREER_SITE_TIME_RANGE = "7d"
CAREER_SITE_EXPERIENCE = ["2-5", "5-10"]

_BODY_COMMON = (
    "Okay, deep breath. 😮‍💨\n\n"
    "You weren't going to read this. You were going to scroll, sip your coffee, and move on. But here's the thing 😏\n\n"
    "**This email wasn't written for you by a human. It was sent by a bot I built from scratch.** 🤖\n"
    "LinkedIn scrapers → Apify → RabbitMQ → SMTP workers → your inbox. 24/7 on my own server. Today, it picked you. Lucky you. 😎\n\n"
    "I could've copy-pasted a template. Instead, I built the thing that copy-pastes for me.\n"
    "Most candidates *send* emails. I *ship software*. You just felt the difference.\n\n"
    "Who am I? A 3+ yr Full Stack Dev. Allergic to boring. Addicted to shipping. No tech I can't learn in 2 weeks, no role I'm too proud to take — FS, frontend, backend, DevOps — just let me build. 🏗️\n\n"
    "Receipts, all live, all mine:\n"
    "🏏 **TPL Mania** — Dream11 built from scratch. Fantasy cricket, live scoring, payments → https://tplmania.org\n"
    "🎮 **TicTacToe Multiplayer** — WebSocket PvP, built in a weekend → https://tictactoe.saitejareddy.online\n"
    "🤖 **Auto Email Sender** — The bot that just hit your inbox. Open source → https://github.com/mintureddy25/auto_email_sender\n"
    "🌐 **Portfolio** → https://saitejareddy.online\n\n"
    "Tech stack? Whatever you're using. I don't marry frameworks — I ship with them, then move on. ⚡\n\n"
    "Give me *any* role where someone owns features idea → prod, and I'll embarrass devs with 2x my XP. Onboard in days. Ship in weeks. 🚀\n\n"
    "If this made you smirk, hit reply. Worst case: you close the tab. Best case: you find your next builder. 🙌\n\n"
    "**Sai Teja Reddy**\n"
    "📍 Hyderabad · ⚡ 3+ yrs · 💼 Immediate joiner\n\n"
    "P.S. Still here? You just finished a cold email a bot delivered. That's me in production. Imagine what I'd do with your codebase. 😎\n"
    "P.P.S. Resume attached. She's thorough."
)

BODY_BY_SOURCE = {
    "hiring_post": "Hi,\n\nI came across your {role} hiring post on LinkedIn and had to reach out.\n" + _BODY_COMMON,
    "people_search": "Hi {name},\n\nI found your profile on LinkedIn and noticed you're in talent acquisition. I'm a Full Stack Developer with 3+ years of experience, actively looking for new opportunities.\n" + _BODY_COMMON,
    "company_employees": "Hi {name},\n\nI noticed {company} is hiring and wanted to reach out directly. I'm a Full Stack Developer with 3+ years of experience.\n" + _BODY_COMMON,
}

# Fallback for any source not in the map
EMAIL_BODY_TEMPLATE = "Hi,\n\nI came across your hiring post on LinkedIn and had to reach out.\n" + _BODY_COMMON
