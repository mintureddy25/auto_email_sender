"""
Monday 10AM cron: re-queue all emails from resend_emails.json
(populated by Sunday cleanup.sh from the week's sent_log.json).
After queueing, clears the file so they don't resend again.
"""

from datetime import datetime

from src.config import RESEND_EMAILS_FILE
from src.collectors.emails import Emails
from src.queue.rabbitmq import publish_batch
from src.utils.file_utils import load_json, save_json


def main():
    print(f"[{datetime.now()}] Resend started")

    emails = load_json(RESEND_EMAILS_FILE)
    if not emails:
        print("  No emails to resend. Done.")
        return

    print(f"  Found {len(emails)} emails to resend")

    publish_batch(Emails, emails)

    # Clear the file so they don't get resent again next week
    save_json(RESEND_EMAILS_FILE, [])
    print(f"[{datetime.now()}] Resend complete — cleared {RESEND_EMAILS_FILE}")


if __name__ == "__main__":
    main()
