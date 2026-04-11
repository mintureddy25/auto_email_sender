import json
import socket
import time
from datetime import datetime

import pika

from src.config import RABBITMQ_URL


def _connect():
    """Build a resilient BlockingConnection.

    - heartbeat=600: slow SMTP sends can't starve pika's single-threaded loop.
    - TCP keepalives: let the OS surface dead sockets as errors (otherwise
      BlockingConnection can silently hang on a half-open socket).
    """
    params = pika.URLParameters(RABBITMQ_URL)
    params.heartbeat = 600
    params.blocked_connection_timeout = 300
    params.socket_timeout = 30
    params.tcp_options = {
        "TCP_KEEPIDLE": 60,
        "TCP_KEEPINTVL": 20,
        "TCP_KEEPCNT": 3,
    }
    return pika.BlockingConnection(params)


def _ensure_queue(channel, data_type):
    """Declare a DLX-wired queue for a DataType. Idempotent.

    If the main queue exists with mismatched args, it's deleted and recreated
    on a fresh channel (safe when the queue is drained continuously).
    """
    queue_name = data_type.queue_name
    dlx_name = data_type.get_dlx()
    failed_queue = data_type.get_failed_queue()

    channel.exchange_declare(exchange=dlx_name, exchange_type="direct", durable=True)
    channel.queue_declare(queue=failed_queue, durable=True)
    channel.queue_bind(exchange=dlx_name, queue=failed_queue, routing_key=failed_queue)

    args = {
        "x-dead-letter-exchange": dlx_name,
        "x-dead-letter-routing-key": failed_queue,
    }
    try:
        channel.queue_declare(queue=queue_name, durable=True, arguments=args)
        return channel
    except pika.exceptions.ChannelClosedByBroker as e:
        if e.reply_code != 406:  # PRECONDITION_FAILED
            raise
        print(f"[migration] '{queue_name}' exists without DLX args - recreating")
        new_channel = channel.connection.channel()
        new_channel.queue_delete(queue=queue_name)
        new_channel.queue_declare(queue=queue_name, durable=True, arguments=args)
        return new_channel


def publish_batch(data_type, items):
    """Publish items to data_type.queue_name (declaring the queue if needed)."""
    if not data_type.queue_name or not items:
        return 0
    connection = _connect()
    channel = connection.channel()
    channel = _ensure_queue(channel, data_type)

    count = 0
    for item in items:
        channel.basic_publish(
            exchange="",
            routing_key=data_type.queue_name,
            body=json.dumps(item),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        count += 1
    connection.close()
    print(f"  Queued {count} items into '{data_type.queue_name}'")
    return count


def consume_multi(routes):
    """Consume many queues in one worker process.

    routes: dict[data_type -> sender_instance]. Declares each queue, registers
    a consumer that dispatches to the matching sender, drains all in one
    blocking loop. Auto-reconnects on any socket/broker failure.
    """
    while True:
        try:
            connection = _connect()
            channel = connection.channel()
            channel.basic_qos(prefetch_count=1)

            for data_type, sender in routes.items():
                channel = _ensure_queue(channel, data_type)

                def make_callback(s):
                    def on_message(ch, method, properties, body):
                        data = json.loads(body)
                        key = data.get(s.data_type.dedup_key, "")
                        print(f"[{datetime.now()}] [{s.name}] Job: {key}", flush=True)
                        try:
                            s.send(data)
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                            print(f"[{datetime.now()}] [{s.name}] SENT {key}", flush=True)
                        except Exception as e:
                            print(f"[{datetime.now()}] [{s.name}] FAILED -> DLQ: {e}", flush=True)
                            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                    return on_message

                channel.basic_consume(
                    queue=data_type.queue_name,
                    on_message_callback=make_callback(sender),
                )
                print(f"[{datetime.now()}] [{sender.name}] consuming '{data_type.queue_name}'",
                      flush=True)

            print(f"[{datetime.now()}] Waiting for jobs...", flush=True)
            channel.start_consuming()

        except (pika.exceptions.AMQPConnectionError,
                pika.exceptions.StreamLostError,
                pika.exceptions.ChannelClosedByBroker,
                pika.exceptions.ConnectionClosedByBroker,
                socket.error) as e:
            print(f"[{datetime.now()}] Connection lost: {e}. Retrying in 10s...", flush=True)
            time.sleep(10)
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] Worker stopped.", flush=True)
            break
        except Exception as e:
            print(f"[{datetime.now()}] Error: {e}. Retrying in 5s...", flush=True)
            time.sleep(5)


def requeue_failed(data_type):
    """Drain data_type's failed queue back into its main queue."""
    failed = data_type.get_failed_queue()
    main = data_type.queue_name
    if not failed or not main:
        print(f"  [{data_type.name}] no queue configured")
        return 0

    connection = _connect()
    channel = connection.channel()
    channel = _ensure_queue(channel, data_type)

    moved = 0
    while True:
        method, properties, body = channel.basic_get(queue=failed, auto_ack=False)
        if method is None:
            break
        channel.basic_publish(
            exchange="",
            routing_key=main,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2),
        )
        channel.basic_ack(delivery_tag=method.delivery_tag)
        moved += 1
    connection.close()
    print(f"  Requeued {moved} messages from '{failed}' -> '{main}'")
    return moved
