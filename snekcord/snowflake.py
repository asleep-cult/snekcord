from __future__ import annotations

import typing
from datetime import datetime

if typing.TYPE_CHECKING:
    from typing_extensions import Self

    from .json import JSONObject

__all__ = ('Snowflake',)

_SNOWFLAKE_EPOCH = 1420070400000

_TIMESTAMP_SHIFT = 22
_WORKER_ID_SHIFT = 17
_PROCESS_ID_SHIFT = 12

_WORKER_ID_MASK = 0x3E0000
_PROCESS_ID_MASK = 0x1F000
_INCREMENT_MASK = 0xFFF


class Snowflake(int):
    @classmethod
    def build(
        cls,
        timestamp: typing.Optional[datetime] = None,
        *,
        worker_id: int = 0,
        process_id: int = 0,
        increment: int = 0,
    ) -> Self:
        if timestamp is None:
            seconds = datetime.utcnow().timestamp()
        else:
            seconds = timestamp.timestamp()

        milliseconds = int((seconds * 1000) - _SNOWFLAKE_EPOCH)

        return cls(
            (milliseconds << _TIMESTAMP_SHIFT)
            | (worker_id << _WORKER_ID_SHIFT)
            | (process_id << _PROCESS_ID_SHIFT)
            | increment
        )

    @classmethod
    def into(cls, data: JSONObject, key: str) -> typing.Optional[Self]:
        value = data.get(key)
        if value is None:
            return None

        value = data[key] = cls(value)
        return value

    @property
    def timestamp(self) -> float:
        return ((self >> _TIMESTAMP_SHIFT) + _SNOWFLAKE_EPOCH) / 1000

    @property
    def worker_id(self) -> int:
        return (self & _WORKER_ID_MASK) >> _WORKER_ID_SHIFT

    @property
    def process_id(self) -> int:
        return (self & _PROCESS_ID_MASK) >> _PROCESS_ID_SHIFT

    @property
    def increment(self) -> int:
        return self & _INCREMENT_MASK

    def to_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp)


class SnowflakeIterator:
    def __init__(self, iterable: typing.Iterable[typing.SupportsInt]) -> None:
        self.iterable = iterable

    def __iter__(self) -> typing.Iterator[Snowflake]:
        return (Snowflake(value) for value in self.iterable)
