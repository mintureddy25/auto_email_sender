"""
24/7 worker: runs every registered sender, each consuming its own queue.

Add a new sender: drop a file in src/senders/ and restart this service.
"""

from datetime import datetime

from src.queue.rabbitmq import consume_multi
from src.senders import get_all as get_senders


def main():
    print(f"[{datetime.now()}] Worker started", flush=True)

    senders = [cls() for cls in get_senders()]
    if not senders:
        print(f"[{datetime.now()}] No senders registered — nothing to do.", flush=True)
        return

    # routes: {DataType -> sender_instance}
    routes = {s.data_type: s for s in senders}
    print(
        f"[{datetime.now()}] Senders: "
        f"{[(s.name, s.data_type.queue_name) for s in senders]}",
        flush=True,
    )

    consume_multi(routes)


if __name__ == "__main__":
    main()
