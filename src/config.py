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
SUBJECT = "Full Stack Developer | 3+ Yrs | React, Next.js, Node.js, Java"

# Data files
DATA_DIR = os.path.join(BASE_DIR, "data")
EMAILS_FILE = os.path.join(DATA_DIR, "emails.json")
SENT_LOG_FILE = os.path.join(DATA_DIR, "sent_log.json")
PHONE_NUMBERS_FILE = os.path.join(DATA_DIR, "phone_numbers.json")
FORM_LINKS_FILE = os.path.join(DATA_DIR, "form_links.json")
JOB_LINKS_FILE = os.path.join(DATA_DIR, "job_links.json")
RESUME_PDF = os.path.join(BASE_DIR, "saitejareddyresume.pdf")

# Scraper config
HIRING_POST_QUERIES = [
    "hiring full stack developer Bangalore",
    "hiring software engineer Bangalore",
    "hiring SDE Bangalore",
]

RECRUITER_TITLES = [
    "Technical Recruiter",
    "HR Manager",
    "Talent Acquisition",
    "Recruiter",
    "Hiring Manager",
]

LOCATIONS = ["Bangalore"]

TARGET_COMPANIES = [
    "https://www.linkedin.com/company/walmart",
    "https://www.linkedin.com/company/cred",
    "https://www.linkedin.com/company/zerodha",
    "https://www.linkedin.com/company/postman",
    "https://www.linkedin.com/company/browserstack",
    "https://www.linkedin.com/company/meesho",
    "https://www.linkedin.com/company/urban-company",
    "https://www.linkedin.com/company/chargebee",
    "https://www.linkedin.com/company/freshworks",
    "https://www.linkedin.com/company/darwinbox",
    "https://www.linkedin.com/company/highradius",
    "https://www.linkedin.com/company/innovaccer",
    "https://www.linkedin.com/company/groww",
    "https://www.linkedin.com/company/slice",
    "https://www.linkedin.com/company/upstox",
    "https://www.linkedin.com/company/cleartax",
    "https://www.linkedin.com/company/razorpayx",
    "https://www.linkedin.com/company/coin-dcx",
    "https://www.linkedin.com/company/cars24",
    "https://www.linkedin.com/company/elasticrun",
    "https://www.linkedin.com/company/lead-square",
    "https://www.linkedin.com/company/khatabook",
    "https://www.linkedin.com/company/acko",
    "https://www.linkedin.com/company/open-financial-technologies",
    "https://www.linkedin.com/company/niyo-solutions",
    "https://www.linkedin.com/company/simpl",
    "https://www.linkedin.com/company/programming",
    "https://www.linkedin.com/company/phonepe-internet",
    "https://www.linkedin.com/company/swiggy",
    "https://www.linkedin.com/company/zomato",
    "https://www.linkedin.com/company/flipkart",
    "https://www.linkedin.com/company/olacabs",
    "https://www.linkedin.com/company/paytm",
    "https://www.linkedin.com/company/dream11",
    "https://www.linkedin.com/company/sharechat",
    "https://www.linkedin.com/company/unacademy",
    "https://www.linkedin.com/company/byjus",
    "https://www.linkedin.com/company/lenskart",
    "https://www.linkedin.com/company/nykaa",
    "https://www.linkedin.com/company/bigbasket",
    "https://www.linkedin.com/company/dunzo",
    "https://www.linkedin.com/company/rapido-bike",
    "https://www.linkedin.com/company/jupiter-money",
    "https://www.linkedin.com/company/indmoney",
    "https://www.linkedin.com/company/smallcase",
    "https://www.linkedin.com/company/delhivery",
    "https://www.linkedin.com/company/zoho",
    "https://www.linkedin.com/company/mindtickle",
    "https://www.linkedin.com/company/hashedin-technologies",
    "https://www.linkedin.com/company/cure-fit",
    "https://www.linkedin.com/company/pharmeasy",
    "https://www.linkedin.com/company/spinny",
    "https://www.linkedin.com/company/udaan-com",
    "https://www.linkedin.com/company/razorpay",
    "https://www.linkedin.com/company/rupeek",
]

MAX_POST_EMAILS = 50
MAX_PEOPLE_EMAILS = 50
MAX_COMPANY_EMAILS = 50

# --- Per-scraper Apify filters (all tunables live here) ---
# hiring_posts
HIRING_MAX_POSTS = 117
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

EMAIL_BODY_TEMPLATE = (
    "Hi,\n\n"
    "I found the {subject} role on LinkedIn and had to reach out.\n"
    "I'm not someone who just writes code — for me, coding is a lifestyle. It's how I think, solve, and live.\n"
    "Quick example: I needed to send recurring messages. Most copy-paste. I built a cron job. That mindset — "
    "finding smart, scalable solutions — is what I bring to every team.\n"
    "Here's some of what I've built recently:\n"
    "🔧 Email Sender Tool (Node.js, Redis, React)\n"
    "✈️ Flight Booking App\n"
    "🏏 Cricket Tournament Platform\n\n"
    "Even this email was sent using my own tool that automates sending personalized emails to recruiters.\n"
    "I thrive on solving real problems and love working across stacks. I learn fast — give me 15–20 days and I'm productive in any tech.\n"
    "Portfolio → https://saitejareddy.online\n\n"
    "If this sounds interesting, I'd love to show you what I've built. Let's connect?\n\n"
    "Best,\n"
    "Sai Teja Reddy\n"
    "P.S. I have attached my resume for your reference."
)
