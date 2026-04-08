import json
import pika
from src.config import RABBITMQ_URL, EMAIL_QUEUE, SUBJECT


def get_channel():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=EMAIL_QUEUE, durable=True)
    return connection, channel


def publish(channel, queue, data):
    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2),
    )


def queue_emails(emails):
    connection, channel = get_channel()
    count = 0
    for entry in emails:
        publish(channel, EMAIL_QUEUE, {
            "email": entry["email"],
            "name": entry.get("name", ""),
            "company": entry.get("company", ""),
            "title": entry.get("title", ""),
            "source": entry.get("source", ""),
            "subject": SUBJECT,
        })
        count += 1
    connection.close()
    print(f"  Queued {count} emails into '{EMAIL_QUEUE}'")
