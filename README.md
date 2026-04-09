# Auto Email Sender

Automated LinkedIn scraper that collects recruiter emails, phone numbers, job application links, and form links — then sends personalized emails with resume attached via RabbitMQ queue.

## Architecture

```
[Cron 9AM + 10:30PM]                [24/7 systemd Service]
run.sh → scrape.py                  auto-email-worker → worker.py
  │                                    │
  ├── Scrape LinkedIn                  ├── Consume RabbitMQ queue
  │   ├── Hiring Posts                 ├── Send email via Gmail SMTP
  │   ├── People Search                └── Log to data/sent_log.json
  │   └── Company Employees
  │
  ├── Save to data/*.json
  │   ├── emails.json
  │   ├── phone_numbers.json
  │   ├── form_links.json
  │   └── job_links.json
  │
  └── Push emails to RabbitMQ
```

## Project Structure

```
auto_email_sender/
├── scrape.py                  # Entry: cron scraper
├── worker.py                  # Entry: 24/7 email sender
├── run.sh                     # Cron runner script
├── setup.sh                   # One-time setup (systemd + cron)
├── requirements.txt
├── .env
│
├── src/
│   ├── config.py              # All config & constants
│   ├── scrapers/
│   │   ├── hiring_posts.py    # LinkedIn post scraper
│   │   ├── people_search.py   # Recruiter profile scraper
│   │   └── company_employees.py
│   ├── senders/
│   │   └── email_sender.py    # Gmail SMTP sender
│   ├── queue/
│   │   └── rabbitmq.py        # RabbitMQ publisher
│   └── utils/
│       ├── file_utils.py      # JSON read/write
│       ├── extractors.py      # Email, phone, URL regex
│       └── dedup.py           # Deduplication helpers
│
├── data/                      # Runtime data (gitignored)
│   ├── emails.json            # All scraped recruiter emails
│   ├── sent_log.json          # Email send history with status
│   ├── phone_numbers.json     # Recruiter phone numbers
│   ├── form_links.json        # Google/Microsoft Forms links
│   └── job_links.json         # Job application links
│
└── logs/                      # Cron logs (gitignored)
```

## Prerequisites

- Python 3.10+
- [Apify](https://apify.com) account (free $5/month)
- [CloudAMQP](https://cloudamqp.com) account (free tier — 1M messages/month)
- Gmail account with App Password

## Setup

### 1. Configure

```bash
cd auto_email_sender
cp .env.example .env
```

Edit `.env` with your credentials:

| Variable | Where to get it |
|----------|----------------|
| `APIFY_TOKEN` | [Apify Console](https://console.apify.com/) → Settings → API Token |
| `RABBITMQ_URL` | [CloudAMQP](https://cloudamqp.com) → Instance → AMQP Details → URL |
| `EMAIL_USER` | Your Gmail address |
| `EMAIL_PASSWORD` | Gmail App Password ([instructions below](#gmail-app-password)) |

### 2. Install and run

```bash
chmod +x setup.sh run.sh
sudo ./setup.sh
```

This will:
- Install Python dependencies
- Create `data/` and `logs/` directories
- Install and start systemd service (`auto-email-worker`) — runs 24/7, survives reboots
- Set up cron jobs for the current user (9AM + 10:30PM scraping)

### 3. Add your resume

Place your resume PDF in the project root. Update the filename in `src/config.py`:

```python
RESUME_PDF = os.path.join(BASE_DIR, "your_resume.pdf")
```

> **Note:** The resume is read from this path and attached to every outgoing email. It is **not** pushed to any external service — it stays local on your machine.

### 4. Customize

Edit `src/config.py` to change:
- Search queries (`HIRING_POST_QUERIES`)
- Target companies (`TARGET_COMPANIES`)
- Recruiter titles (`RECRUITER_TITLES`)
- Locations (`LOCATIONS`)
- Email subject and body template

## Manual Run

```bash
# Scrape LinkedIn and queue emails
python3 scrape.py

# Or use the cron runner script
./run.sh

# Start worker manually (if not using systemd)
python3 worker.py
```

## Data Collection

| Source | What it collects |
|--------|-----------------|
| **Hiring Posts** | Emails, phone numbers, form links, job links from post text |
| **People Search** | Recruiter emails and phone numbers from profiles |
| **Company Employees** | HR/Recruiter emails and phone numbers from target companies |

## Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification**
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Generate a password for "Mail"
5. Use the 16-character password in `.env`

## Service Commands

```bash
# Check worker status
sudo systemctl status auto-email-worker

# View worker logs
tail -f worker.log

# Restart worker
sudo systemctl restart auto-email-worker

# Stop worker
sudo systemctl stop auto-email-worker

# View cron logs
ls -lt logs/
```

## Apify Actors Used

| Actor | Purpose |
|-------|---------|
| [harvestapi/linkedin-post-search](https://apify.com/harvestapi/linkedin-post-search) | Scrape LinkedIn hiring posts |
| [harvestapi/linkedin-profile-search](https://apify.com/harvestapi/linkedin-profile-search) | Search recruiters with email enrichment |
| [harvestapi/linkedin-company-employees](https://apify.com/harvestapi/linkedin-company-employees) | Find HR at specific companies |
