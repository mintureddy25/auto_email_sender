# Auto Email Sender

Automated LinkedIn recruiter email scraper + sender. Scrapes recruiter/HR emails from LinkedIn hiring posts, people search, and company employees using Apify, queues them in Redis, and a 24/7 worker sends personalized emails with your resume attached.

## Architecture

```
┌──────────────────────────────────────────────────────┐
│  CRON (Daily 9AM)                                    │
│  scrape_and_queue.py                                 │
│                                                      │
│  Source 1: LinkedIn Hiring Posts                     │
│    → Scrapes posts with "hiring developer" etc.      │
│    → Extracts emails from post text (regex)          │
│                                                      │
│  Source 2: LinkedIn People Search                    │
│    → Searches for Recruiters/HR/Talent Acquisition   │
│    → Returns emails via email enrichment             │
│                                                      │
│  Source 3: Company Employees                         │
│    → Finds HR/Recruiters at target companies         │
│    → Returns emails via email enrichment             │
│                                                      │
│  → Deduplicates against already sent emails          │
│  → Pushes NEW emails into Redis queue                │
└──────────────────────┬───────────────────────────────┘
                       │ rpush → Redis queue
                       ▼
┌──────────────────────────────────────────────────────┐
│  24/7 WORKER (systemd service)                       │
│  queue_worker.py                                     │
│                                                      │
│  → blpop waits for jobs (instant pickup, no polling) │
│  → Sends email + resume back-to-back (no delay)      │
│  → Logs to sent_log.json                             │
│  → Auto-restarts on crash/reboot                     │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  CRON (Daily 9AM)                                    │
│  generate_report.py                                  │
│                                                      │
│  → New Excel sheet per day: reports/sent_YYYY-MM-DD  │
│  → Master sheet: reports/all_sent_emails.xlsx        │
└──────────────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.10+
- Redis instance (free tier at [Redis Cloud](https://redis.com/try-free/))
- Apify account (free $5/month at [apify.com](https://apify.com))
- Gmail account with App Password

## Setup

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd auto_email_sender
pip install -r requirements.txt
```

### 2. Create `.env` file

```bash
cp .env.example .env
```

Fill in your credentials:

| Variable | Where to get it |
|----------|----------------|
| `APIFY_TOKEN` | [Apify Console](https://console.apify.com/) → Settings → Integrations → API Token |
| `REDIS_HOST` | Your Redis cloud instance host |
| `REDIS_PORT` | Your Redis cloud instance port |
| `REDIS_USERNAME` | Usually `default` |
| `REDIS_PASSWORD` | Your Redis instance password |
| `EMAIL_USER` | Your Gmail address |
| `EMAIL_PASSWORD` | Gmail App Password (NOT your regular password) |
| `EMAIL_SMTP_SERVER` | `smtp.gmail.com` |
| `EMAIL_SMTP_PORT` | `587` |

#### Getting Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already enabled
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Generate a new app password for "Mail"
5. Use that 16-character password in `.env`

### 3. Add your resume

Place your resume PDF in the project root:

```bash
cp /path/to/your/resume.pdf ./chappeta_sai_teja_reddy_resume.pdf
```

Update the filename in `queue_worker.py` if your file is named differently:
```python
RESUME_PDF = os.path.join(BASE_DIR, "your_resume.pdf")
```

### 4. Customize search queries and target companies

Edit `scrape_and_queue.py`:

```python
# LinkedIn post search queries
HIRING_POST_QUERIES = [
    "hiring full stack developer India",
    "hiring software engineer India",
    # Add your own...
]

# Target companies for HR/recruiter email scraping
TARGET_COMPANIES = [
    "https://www.linkedin.com/company/google",
    # Add your target companies...
]

# Recruiter job titles to search
RECRUITER_TITLES = [
    "Technical Recruiter",
    "HR Manager",
    # Add more...
]

# Locations
LOCATIONS = ["India", "Bangalore", "Hyderabad", "Pune", "Delhi", "Mumbai"]
```

### 5. Customize email text

Edit the `get_email_body()` function in `queue_worker.py` with your own message, portfolio link, and highlights.

## Running

### Manual run (test)

```bash
# Step 1: Scrape emails and push to Redis queue
python3 scrape_and_queue.py

# Step 2: Start worker to send emails (runs continuously)
python3 queue_worker.py

# Step 3: Generate Excel report
python3 generate_report.py
```

### Production setup (cron + systemd)

```bash
# Install systemd service (runs worker 24/7, auto-restarts on reboot)
sudo bash setup.sh
```

This does:
- Installs `queue_worker.py` as a systemd service (24/7, auto-restart)
- Sets up cron job at 9AM daily for scraping + report generation

#### Manual cron + worker setup

```bash
# Start worker in background
nohup python3 queue_worker.py >> worker.log 2>&1 &

# Add cron job
crontab -e
# Add this line:
0 9 * * * /path/to/auto_email_sender/run.sh
```

### Check status

```bash
# Worker service status
sudo systemctl status auto-email-worker

# Worker logs
tail -f worker.log

# Queue length
python3 -c "
import redis
r = redis.StrictRedis(host='YOUR_HOST', port=YOUR_PORT, decode_responses=True, username='default', password='YOUR_PASS')
print('Queue:', r.llen('auto_email_queue'))
"

# Sent email count
python3 -c "
import json
log = json.load(open('sent_log.json'))
sent = [e for e in log if e['status'] == 'sent']
print(f'Sent: {len(sent)}')
"
```

## File Structure

```
auto_email_sender/
├── .env.example                 # Environment template
├── .env                         # Your credentials (git ignored)
├── .gitignore
├── requirements.txt
├── README.md
│
├── scrape_and_queue.py          # Cron: scrapes LinkedIn → Redis queue
├── queue_worker.py              # 24/7: Redis queue → sends emails
├── generate_report.py           # Cron: generates daily Excel reports
├── run.sh                       # Cron runner script
├── setup.sh                     # One-time systemd + cron setup
├── auto-email-worker.service    # systemd service file
│
├── chappeta_sai_teja_reddy_resume.pdf  # Resume attachment
│
├── emails.json                  # All scraped emails (git ignored)
├── sent_log.json                # Send history (git ignored)
├── worker.log                   # Worker logs (git ignored)
├── logs/                        # Cron run logs (git ignored)
└── reports/                     # Excel reports (git ignored)
    ├── sent_emails_2026-04-07.xlsx
    └── all_sent_emails.xlsx
```

## Cost

| Source | Free tier limit | Emails/run | Cost |
|--------|----------------|------------|------|
| Hiring Posts | **No limit** | ~50 | ~$0.80 |
| People Search | 25 profiles | ~10-14 | ~$0.25 |
| Company Employees | 25 profiles | ~8-10 | ~$0.12 |
| **Total** | | **~67-74/day** | **~$1.17/day** |

With Apify paid plan ($49/month): People Search and Company Employees limits are removed, 100+ emails/day.

## Apify Actors Used

| Actor | Purpose |
|-------|---------|
| [harvestapi/linkedin-post-search](https://apify.com/harvestapi/linkedin-post-search) | Scrape LinkedIn hiring posts |
| [harvestapi/linkedin-profile-search](https://apify.com/harvestapi/linkedin-profile-search) | Search recruiters/HR with email enrichment |
| [harvestapi/linkedin-company-employees](https://apify.com/harvestapi/linkedin-company-employees) | Find HR at specific companies with emails |
