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
PENDING_QUEUE_FILE = os.path.join(DATA_DIR, "pending_queue.json")

# Static assets
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
RESUME_PDF = os.path.join(ASSETS_DIR, "saitejareddyresume.pdf")

# Scraper enable/disable — set False to skip a scraper without deleting the file
SCRAPER_ENABLED = {
    "hiring_posts": True,
    "people_search": False,
    "company_employees": False,
    "linkedin_jobs": False,
    "career_sites": False,
    "naukri_jobs": False,
    "indeed_jobs": False,
}

# Scraper config
HIRING_POST_QUERIES = [
    "hiring full stack developer Pune",
    "hiring full stack developer Hyderabad",
    "hiring full stack developer Bengaluru",
    "hiring software engineer Pune",
    "hiring software engineer Hyderabad",
    "hiring software engineer Bengaluru",
    "hiring SDE Pune",
    "hiring SDE Hyderabad",
    "hiring SDE Bengaluru",
]

RECRUITER_TITLES = [
    "Technical Recruiter",
    "HR Manager",
    "Talent Acquisition",
    "Recruiter",
    "Hiring Manager",
]

LOCATIONS = ["Bangalore", "Hyderabad", "Pune"]

TARGET_COMPANIES = [
    # Big tech India offices
    "https://www.linkedin.com/company/google",
    "https://www.linkedin.com/company/microsoft",
    "https://www.linkedin.com/company/amazon",
    "https://www.linkedin.com/company/meta",
    "https://www.linkedin.com/company/adobe",
    "https://www.linkedin.com/company/atlassian",
    "https://www.linkedin.com/company/nvidia",
    "https://www.linkedin.com/company/salesforce",
    "https://www.linkedin.com/company/oracle",
    "https://www.linkedin.com/company/intuit",
    # Indian unicorns / scale-ups (not in previous list)
    "https://www.linkedin.com/company/swiggy",
    "https://www.linkedin.com/company/zerodha",
    "https://www.linkedin.com/company/dream11",
    "https://www.linkedin.com/company/phonepe",
    "https://www.linkedin.com/company/paytm",
    "https://www.linkedin.com/company/flipkart",
    "https://www.linkedin.com/company/nykaa",
    "https://www.linkedin.com/company/byjus",
    "https://www.linkedin.com/company/ola-cabs",
    # AI / DevTools / Modern SaaS (different from previous)
    "https://www.linkedin.com/company/devrev",
    "https://www.linkedin.com/company/uniphore",
    "https://www.linkedin.com/company/mindtickle",
    "https://www.linkedin.com/company/amagicorp",
    "https://www.linkedin.com/company/observeai",
    # Fintech (different from previous)
    "https://www.linkedin.com/company/juspay",
    "https://www.linkedin.com/company/acko",
    "https://www.linkedin.com/company/cleartax-in",
    "https://www.linkedin.com/company/signzy",
    "https://www.linkedin.com/company/m2p-fintech",
    # Mid-stage product startups
    "https://www.linkedin.com/company/hyperverge",
    "https://www.linkedin.com/company/fyle",
    "https://www.linkedin.com/company/zenoti",
    "https://www.linkedin.com/company/dripcapital",
    "https://www.linkedin.com/company/fynd",
    "https://www.linkedin.com/company/wati-io",
]

MAX_POST_EMAILS = 50
MAX_PEOPLE_EMAILS = 50
MAX_COMPANY_EMAILS = 50

# --- Per-scraper Apify filters (all tunables live here) ---
# hiring_posts
HIRING_MAX_POSTS = 120
HIRING_POSTED_LIMIT = "week"
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
JOBS_POSTED_LIMIT = "week"
JOBS_MAX_ITEMS = 50
JOBS_SORT_BY = "date"
JOBS_EXPERIENCE_LEVELS = ["entry", "associate", "mid-senior"]
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

# jobspy scrapers (naukri_jobs, indeed_jobs) - free, no API key
JOBSPY_SEARCH_TERMS = [
    "full stack developer",
    "software engineer",
    "nodejs developer",
    "react developer",
]
JOBSPY_LOCATIONS = ["Bangalore", "Hyderabad", "Pune"]
JOBSPY_RESULTS_PER_QUERY = 30
JOBSPY_HOURS_OLD = 24

_BODY_COMMON = (
    "Okay, deep breath. 😮‍💨\n\n"
    "Take a sip of coffee. But here's the thing 😏\n\n"
    "I built a project that scrapes LinkedIn posts and emails, and sends emails automatically. **This email was also sent using my project.** 🤖\n\n"
    "Receipts, all live, all mine:\n"
    "🏏 **TPL Mania** — Dream11 built from scratch. Fantasy cricket, live scoring, payments → https://tplmania.org\n"
    "🎮 **TicTacToe Multiplayer** — WebSocket PvP, built in a weekend → https://tictactoe.saitejareddy.online\n"
    "🤖 **Auto Email Sender** — The bot that just hit your inbox. Open source → https://github.com/mintureddy25/auto_email_sender\n"
    "🌐 **Portfolio** → https://saitejareddy.online\n\n"
    "Tech stack? Whatever you're using. I don't marry frameworks — I ship with them, then move on. ⚡\n\n"
    "**Sai Teja Reddy**\n"
    "📍 Hyderabad · ⚡ 3+ yrs · 💼 Immediate joiner"
)

BODY_BY_SOURCE = {
    "hiring_post": "Hi,\n\nI came across your {role} hiring post on LinkedIn and had to reach out.\n" + _BODY_COMMON,
    "people_search": "Hi {name},\n\nI found your profile on LinkedIn and noticed you're in talent acquisition. I'm a Full Stack Developer with 3+ years of experience, actively looking for new opportunities.\n" + _BODY_COMMON,
    "company_employees": "Hi {name},\n\nI noticed {company} is hiring and wanted to reach out directly. I'm a Full Stack Developer with 3+ years of experience.\n" + _BODY_COMMON,
}

# Fallback for any source not in the map
EMAIL_BODY_TEMPLATE = "Hi,\n\nI came across your hiring post on LinkedIn and had to reach out.\n" + _BODY_COMMON
