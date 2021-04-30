from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, Union


class Snowflake(int):
    __slots__ = ()

    DISCORD_EPOCH = 1420070400000

    TIMESTAMP_SHIFT = 22
    WORKER_ID_SHIFT = 17
    PROCESS_ID_SHIFT = 12

    WORKER_ID_MASK = 0x3E0000
    PROCESS_ID_MASK = 0x1F000
    INCREMENT_MASK = 0xFFF

    @classmethod
    def build(cls, timestamp: Optional[Union[datetime, float]] = None,
              worker_id: int = 0, process_id: int = 0,
              increment: int = 0) -> Snowflake:
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        elif isinstance(timestamp, datetime):
            timestamp = timestamp.timestamp()
        elif not isinstance(timestamp, float):
            raise TypeError(
                'Expected datetime, float or None for timestamp, '
                f'got {timestamp.__class__.__name__!r}')

        timestamp = int((timestamp * 1000) - cls.DISCORD_EPOCH)

        return cls((timestamp << cls.TIMESTAMP_SHIFT)
                   | (worker_id << cls.WORKER_ID_SHIFT)
                   | (process_id << cls.PROCESS_ID_SHIFT)
                   | increment)

    @classmethod
    def try_snowflake(cls, o: Any) -> Union[Snowflake, Any]:
        from ..objects.base import BaseObject

        if isinstance(o, BaseObject):
            return o.id

        try:
            return cls(o)
        except Exception:
            return o

    @property
    def datetime(self) -> datetime:
        return datetime.fromtimestamp(((self >> self.TIMESTAMP_SHIFT)
                                      + self.DISCORD_EPOCH) / 1000)

    @property
    def worker_id(self) -> int:
        return (self & self.WORKER_ID_MASK) >> self.WORKER_ID_SHIFT

    @property
    def process_id(self) -> int:
        return (self & self.PROCESS_ID_MASK) >> self.PROCESS_ID_SHIFT

    @property
    def increment(self) -> int:
        return self & self.INCREMENT_MASK
