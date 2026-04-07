"""
24/7 Redis Queue Worker - watches 'auto_email_queue' and sends emails instantly.
Runs as a systemd service, auto-starts on boot/restart.
Logs sent emails to sent_log.json for report generation.
"""

import json
import os
import smtplib
import time
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import redis
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Redis
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Email
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT"))

RESUME_PDF = os.path.join(BASE_DIR, "chappeta_sai_teja_reddy_resume.pdf")
SENT_LOG_FILE = os.path.join(BASE_DIR, "sent_log.json")
QUEUE_NAME = "auto_email_queue"

# Redis client
client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
)


def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return []


def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def send_email(email, subject):
    """Send email with same text as send_email/emailScript/emailSender.py"""
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = email
    msg["Subject"] = subject

    body = (
        "Hi,\n\n"
        f"I found the {subject} role on LinkedIn and had to reach out.\n"
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

    msg.attach(MIMEText(body, "plain"))

    # Attach resume
    if os.path.exists(RESUME_PDF):
        with open(RESUME_PDF, "rb") as pdf_file:
            pdf_attachment = MIMEApplication(pdf_file.read(), _subtype="pdf")
            pdf_attachment.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(RESUME_PDF)}"',
            )
            msg.attach(pdf_attachment)
    else:
        print(f"[ERROR] Resume PDF not found: {RESUME_PDF}")
        return False

    with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)

    return True


def log_sent(email_data, status):
    """Append to sent_log.json"""
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


def process_jobs():
    """Continuously watch Redis queue and send emails"""
    print(f"[{datetime.now()}] Queue worker started. Watching '{QUEUE_NAME}'...")
    print(f"[{datetime.now()}] Redis: {REDIS_HOST}:{REDIS_PORT}")
    print(f"[{datetime.now()}] Waiting for jobs...\n")

    while True:
        try:
            # blpop blocks until a job is available (timeout=0 means wait forever)
            job = client.blpop(QUEUE_NAME, timeout=0)

            if job:
                data = job[1]
                email_data = json.loads(data)
                email = email_data["email"]
                subject = email_data.get("subject", "Full Stack Developer | 3+ Yrs | React, Next.js, Node.js, Java")

                print(f"[{datetime.now()}] Job received: {email}")

                try:
                    send_email(email, subject)
                    print(f"[{datetime.now()}] SENT to {email}")
                    log_sent(email_data, "sent")
                except Exception as e:
                    print(f"[{datetime.now()}] FAILED {email}: {e}")
                    log_sent(email_data, "failed")

        except redis.ConnectionError as e:
            print(f"[{datetime.now()}] Redis connection lost: {e}. Retrying in 10s...")
            time.sleep(10)
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] Worker stopped.")
            break
        except Exception as e:
            print(f"[{datetime.now()}] Unexpected error: {e}. Retrying in 5s...")
            time.sleep(5)


if __name__ == "__main__":
    process_jobs()
