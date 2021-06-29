from __future__ import annotations

import typing as t
from datetime import datetime

from ..typedefs import SnowflakeConvertible

__all__ = ('Snowflake',)


class Snowflake(int):
    SNOWFLAKE_EPOCH: t.ClassVar[int]

    TIMESTAMP_SHIFT: t.ClassVar[int]
    WORKER_ID_SHIFT: t.ClassVar[int]
    PROCESS_ID_SHIFT: t.ClassVar[int]

    WORKER_ID_MASK: t.ClassVar[int]
    PROCESS_ID_MASK: t.ClassVar[int]
    INCREMENT_MASK: t.ClassVar[int]

    @classmethod
    def build(cls, timestamp: datetime | float | None = ...,
              worker_id: int = ..., process_id: int = ...,
              increment: int = ...) -> Snowflake: ...

    @classmethod
    def try_snowflake(cls, obj: SnowflakeConvertible) -> Snowflake: ...

    @classmethod
    def try_snowflake_set(cls, objs: t.Iterable[SnowflakeConvertible]
                          ) -> set[Snowflake]: ...

    @property
    def timestamp(self) -> float: ...

    @property
    def time(self) -> datetime: ...

    @property
    def worker_id(self) -> int: ...

    @property
    def process_id(self) -> int: ...

    @property
    def increment(self) -> int: ...
