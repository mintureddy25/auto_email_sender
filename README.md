# Auto Email Sender

Plug-and-play LinkedIn scraping + outbound pipeline. Scrapers collect things
(emails, phones, form links, job links, …), push them through per-type
RabbitMQ queues, and senders drain each queue 24/7. Every moving part is a
single file drop-in — no central glue code.

## Architecture

```
[Cron 10AM daily]                             [24/7 systemd Service]
run.sh → scrape.py                            auto-email-worker → worker.py
  │                                               │
  ├── src/scrapers/*            (registry)        ├── src/senders/*   (registry)
  │    each one feeds a                           │    each one drains its
  │    collector via                              │    collector's queue
  │    result.add("emails", …)                    │
  │                                               └── reconnects on any
  ├── src/collectors/*          (registry)            RabbitMQ / socket error
  │    declares a data type:
  │       name, storage file,
  │       dedup key, queue name
  │
  ├── persist → data/*.json
  └── publish → RabbitMQ per collector

[Cron Sunday 4AM]
cleanup.sh
  ├── truncate worker.log
  ├── delete logs/cron_*.log  older than 7 days
  └── reset data/sent_log.json
```

Three registries, each auto-discovered from its folder:

| Folder | What's in it | What a registered file does |
|---|---|---|
| `src/collectors/` | **Data types** — emails, phones, form_links, job_links | Declares where to store, how to dedup, which queue (if any) |
| `src/scrapers/` | **Collection logic** — LinkedIn posts, profile search, company employees | Reads Apify actors, appends items to a `ScrapeResult`, dedups via a shared `SeenSet` |
| `src/senders/` | **Delivery logic** — email sender (more later) | Consumes from its collector's queue and ships each job |

## Project Structure

```
auto_email_sender/
├── scrape.py            # Entry: cron scraper (drives the registries)
├── worker.py            # Entry: 24/7 sender worker (drives the registries)
├── run.sh               # Cron wrapper for scrape.py
├── cleanup.sh           # Weekly log rotator (Sunday 4am)
├── setup.sh             # One-shot install: systemd service + cron entries
├── requeue_failed.py    # Drain every failed queue back into its main queue
├── requirements.txt
├── .env.example
│
├── src/
│   ├── config.py                # All tunables live here (queries, queues, filters)
│   │
│   ├── collectors/              # DATA TYPES — drop a file to add one
│   │   ├── base.py              #   DataType: name, storage_file, dedup_key, queue_name
│   │   ├── emails.py            #   Emails      → auto_email_queue
│   │   ├── phones.py            #   Phones      → store-only (no queue)
│   │   ├── form_links.py        #   FormLinks   → store-only
│   │   └── job_links.py         #   JobLinks    → store-only
│   │
│   ├── scrapers/                # SCRAPERS — drop a file to add one
│   │   ├── base.py              #   BaseScraper, ScrapeResult, SeenSet
│   │   ├── hiring_posts.py      #   LinkedIn hiring posts (harvestapi)
│   │   ├── people_search.py     #   LinkedIn profile search
│   │   └── company_employees.py #   LinkedIn company employees
│   │
│   ├── senders/                 # SENDERS — drop a file to add one
│   │   ├── base.py              #   BaseSender: name + data_type + send(job)
│   │   └── email_sender.py      #   EmailSender (Gmail SMTP + resume attachment)
│   │
│   ├── queue/
│   │   └── rabbitmq.py          # Resilient pika wrapper (heartbeat, keepalive,
│   │                            #   publish_batch, consume_multi, requeue_failed)
│   │
│   └── utils/
│       ├── file_utils.py        # JSON read/write
│       ├── extractors.py        # Email, phone, URL regex
│       ├── url_resolver.py      # Short-link resolver
│       └── sent_log.py          # Append to sent_log.json after a send
│
├── data/                 # Runtime state (gitignored)
│   ├── emails.json       # Master email list (dedup source, never wiped)
│   ├── sent_log.json     # Send history (wiped weekly by cleanup.sh)
│   ├── phone_numbers.json
│   ├── form_links.json
│   └── job_links.json
│
└── logs/                 # Cron + cleanup logs (gitignored)
```

## Prerequisites

- Python 3.10+
- [Apify](https://apify.com) account (free tier works)
- [CloudAMQP](https://cloudamqp.com) account (free tier — 1M messages/month)
- Gmail account with App Password

## Setup

### 1. Configure environment

```bash
cd auto_email_sender
cp .env.example .env
```

Edit `.env`:

| Variable | Where to get it |
|----------|----------------|
| `APIFY_TOKEN` | Apify Console → Settings → API Token |
| `RABBITMQ_URL` | CloudAMQP → Instance → AMQP Details → URL |
| `EMAIL_USER` | Your Gmail address |
| `EMAIL_PASSWORD` | Gmail [App Password](#gmail-app-password) |

### 2. Add your resume

Place your resume PDF in the project root and update the filename in `src/config.py`:

```python
RESUME_PDF = os.path.join(BASE_DIR, "your_resume.pdf")
```

The PDF stays local — attached to every outbound email, never uploaded anywhere.

### 3. Customize filters in `src/config.py`

All tunables live here, grouped by scraper:

```python
# Shared
LOCATIONS = ["Pune"]
RECRUITER_TITLES = [...]
TARGET_COMPANIES = [...]
SUBJECT = "..."

# hiring_posts
HIRING_POST_QUERIES = ["hiring full stack developer Pune", ...]
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

# Queue names (each DataType owns its own queue + DLX + failed queue)
EMAIL_QUEUE = "auto_email_queue"
EMAIL_DLX = "auto_email_dlx"
EMAIL_FAILED_QUEUE = "auto_email_failed"
```

### 4. Install

```bash
chmod +x setup.sh run.sh cleanup.sh
sudo ./setup.sh
```

This will:

- Install Python dependencies
- Create `data/` and `logs/`
- Install and start the `auto-email-worker` systemd service (24/7, auto-restart,
  `PYTHONUNBUFFERED=1`, resilient pika heartbeat + TCP keepalives)
- Install three cron jobs for your user:
  - `0 10 * * *` → scrape (10 AM daily)
  - `0 4 * * 0` → cleanup (Sunday 4 AM)
  - `0 10 * * 1` → resend (Monday 10 AM)

## Extending

### Add a new scraper

Drop a file in `src/scrapers/`:

```python
# src/scrapers/twitter_jobs.py
from src.scrapers import register
from src.scrapers.base import BaseScraper, ScrapeResult, SeenSet

@register
class TwitterJobsScraper(BaseScraper):
    name = "twitter_jobs"

    def run(self, seen: SeenSet) -> ScrapeResult:
        result = ScrapeResult()
        for tweet in fetch_tweets():
            email = extract_email(tweet)
            if email and not seen.has("emails", email):
                result.add("emails", {"email": email, "source": "twitter"})
                seen.add("emails", email)
        return result
```

No edits to `scrape.py`. The next cron run picks it up.

### Add a new data type

Drop a file in `src/collectors/`:

```python
# src/collectors/whatsapp_msgs.py
from src.collectors import register
from src.collectors.base import DataType
from src.config import WHATSAPP_MSGS_FILE, WHATSAPP_QUEUE, WHATSAPP_DLX, WHATSAPP_FAILED_QUEUE

@register
class WhatsAppMsgs(DataType):
    name = "whatsapp_msgs"
    storage_file = WHATSAPP_MSGS_FILE
    dedup_key = "phone"
    queue_name = WHATSAPP_QUEUE     # omit if store-only
    dlx_name = WHATSAPP_DLX
    failed_queue_name = WHATSAPP_FAILED_QUEUE
```

Add the paths and queue names to `src/config.py`. Scrapers can now
`result.add("whatsapp_msgs", {...})` and items will auto-publish to the
new queue at the end of each run.

### Add a new sender

Drop a file in `src/senders/`:

```python
# src/senders/whatsapp.py
from src.collectors.whatsapp_msgs import WhatsAppMsgs
from src.senders import register
from src.senders.base import BaseSender

@register
class WhatsAppSender(BaseSender):
    name = "whatsapp"
    data_type = WhatsAppMsgs

    def send(self, job: dict) -> None:
        twilio_client.messages.create(
            to=job["phone"],
            body=job["message"],
            from_=TWILIO_WHATSAPP_FROM,
        )
```

Restart the worker: `sudo systemctl restart auto-email-worker`. It now
consumes `auto_email_queue` AND `auto_whatsapp_queue` in a single pika loop,
each acking / failing to its own DLX independently.

## Manual Run

```bash
# Scrape once
python3 scrape.py

# Run the cron wrapper (with logging)
./run.sh

# Start the worker in the foreground (bypasses systemd)
python3 worker.py

# Drain every failed queue back into its main queue
python3 requeue_failed.py

# Manually trigger cleanup
./cleanup.sh
```

## Service Commands

```bash
# Worker status + logs
sudo systemctl status auto-email-worker
tail -f worker.log

# Restart (after adding a new sender)
sudo systemctl restart auto-email-worker

# Inspect queue depth + consumer count from the outside
python3 -c "
import pika, os
from dotenv import load_dotenv; load_dotenv()
c = pika.BlockingConnection(pika.URLParameters(os.getenv('RABBITMQ_URL'))).channel()
r = c.queue_declare(queue='auto_email_queue', durable=True, passive=True)
print(f'messages={r.method.message_count}, consumers={r.method.consumer_count}')
"
```

## Reliability Notes

The worker has bit us once before with a silent hang. The current setup
defends against it on four layers:

1. **pika heartbeat = 600s** — slow SMTP sends can't starve the heartbeat loop.
2. **TCP keepalives** (60s idle, 20s × 3 probes) — the OS forces half-open
   sockets to surface an error, so pika sees the disconnect and reconnects.
3. **Catch every socket-death error** — `AMQPConnectionError`, `StreamLostError`,
   `ChannelClosedByBroker`, `ConnectionClosedByBroker`, `socket.error`.
4. **`PYTHONUNBUFFERED=1` + `flush=True`** — logs hit disk immediately, so
   a hung worker can't hide behind a stale buffer.

On top of that, systemd runs the service with `Restart=always` / `RestartSec=10`
so a hard crash self-heals in 10 seconds.

## Log Rotation

| File | Policy | Driven by |
|---|---|---|
| `worker.log` | Truncated in place every Sunday 4 AM | `cleanup.sh` (cron) |
| `logs/cron_*.log` | Deleted if older than 7 days | `run.sh` after every run + `cleanup.sh` |
| `data/sent_log.json` | Reset to `[]` every Sunday 4 AM | `cleanup.sh` |
| `logs/cleanup.log` | Tail-capped to ~20 runs | `cleanup.sh` |

Dedup still works after `sent_log.json` is wiped because `Emails.load_seen()`
also reads `data/emails.json`, which is never cleaned.

## Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification**
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Generate a password for "Mail"
5. Paste the 16-character password into `EMAIL_PASSWORD` in `.env`

## Apify Actors Used

| Actor | Used by |
|-------|---------|
| [harvestapi/linkedin-post-search](https://apify.com/harvestapi/linkedin-post-search) | `src/scrapers/hiring_posts.py` |
| [harvestapi/linkedin-profile-search](https://apify.com/harvestapi/linkedin-profile-search) | `src/scrapers/people_search.py` |
| [harvestapi/linkedin-company-employees](https://apify.com/harvestapi/linkedin-company-employees) | `src/scrapers/company_employees.py` |
