from __future__ import annotations

import math
import typing
from datetime import datetime

if typing.TYPE_CHECKING:
    from typing_extensions import Self

__all__ = ('Snowflake', 'SnowflakeCouple')

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


class SnowflakeCouple(int):
    # Taken from https://stackoverflow.com/a/42333590

    def __new__(cls, high: int, low: int) -> Self:
        if high < 0 or low < 0:
            raise ValueError('low and high should be >= 0')

        x = high * 2
        y = low * 2
        z = (x * x + x + y) if x >= y else (x + y * y)

        return int.__new__(SnowflakeCouple, z // 2)

    def __repr__(self) -> str:
        return f'SnowflakeCouple({self.high}, {self.low})'

    @property
    def high(self) -> Snowflake:
        z = self * 2

        s = math.isqrt(z)
        if z - s * s < s:
            x = z - s * s
        else:
            x = s

        return Snowflake(x // 2)

    @property
    def low(self) -> Snowflake:
        z = self * 2

        s = math.isqrt(z)
        if z - s * s < s:
            y = s
        else:
            y = z - s * s - s

        return Snowflake(y // 2)
