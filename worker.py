"""
24/7 RabbitMQ Worker - consumes email queue and sends emails.
Runs as a systemd service.
"""

import json
import time
from datetime import datetime

import pika

from src.config import RABBITMQ_URL, EMAIL_QUEUE, SENT_LOG_FILE
from src.senders import email_sender
from src.utils.file_utils import load_json, save_json


def log_sent(email_data, status):
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


def on_email(ch, method, properties, body):
    job = json.loads(body)
    email = job["email"]
    subject = job.get("subject", "Full Stack Developer | 3+ Yrs | React, Next.js, Node.js, Java")
    print(f"[{datetime.now()}] Email: {email}")

    try:
        email_sender.send(email, subject)
        print(f"[{datetime.now()}] SENT {email}")
        log_sent(job, "sent")
    except Exception as e:
        print(f"[{datetime.now()}] FAILED {email}: {e}")
        log_sent(job, "failed")

    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    print(f"[{datetime.now()}] Worker started")

    while True:
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            channel.queue_declare(queue=EMAIL_QUEUE, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=EMAIL_QUEUE, on_message_callback=on_email)

            print(f"[{datetime.now()}] Waiting for jobs on '{EMAIL_QUEUE}'...")
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            print(f"[{datetime.now()}] Connection lost: {e}. Retrying in 10s...")
            time.sleep(10)
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] Worker stopped.")
            break
        except Exception as e:
            print(f"[{datetime.now()}] Error: {e}. Retrying in 5s...")
            time.sleep(5)


if __name__ == "__main__":
    main()
