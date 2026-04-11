"""
One-shot script: drain every DataType's failed queue back into its main queue.
Use after fixing whatever caused the failures (e.g. missing resume PDF).
"""

from src.queue.rabbitmq import requeue_failed
from src.collectors import get_all as get_types


if __name__ == "__main__":
    total = 0
    for t in get_types():
        if t.queue_name:
            total += requeue_failed(t)
    print(f"  Total requeued: {total}")
