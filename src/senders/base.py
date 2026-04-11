"""BaseSender: each sender consumes from its own queue.

Adding a new sender:
  1. Create src/senders/<your_name>.py
  2. Subclass BaseSender, decorate with @register, set data_type
  3. Implement send(job)
Worker picks it up automatically at next restart.
"""

from typing import Type

from src.collectors.base import DataType


class BaseSender:
    name: str = ""
    data_type: Type[DataType] = None

    @property
    def queue_name(self) -> str:
        return self.data_type.queue_name

    def send(self, job: dict) -> None:
        raise NotImplementedError
