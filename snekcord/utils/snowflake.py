from __future__ import annotations

from datetime import datetime
from typing import Iterable, Set, SupportsInt, TYPE_CHECKING, TypeVar, Union, overload

if TYPE_CHECKING:
    from ..objects.baseobject import BaseObject

    T = TypeVar('T')
    ConvertableToInt = Union[SupportsInt, str]
    SnowflakeType = Union[ConvertableToInt, BaseObject]

__all__ = ('Snowflake',)


class Snowflake(int):
    __slots__ = ()

    SNOWFLAKE_EPOCH = 1420070400000

    TIMESTAMP_SHIFT = 22
    WORKER_ID_SHIFT = 17
    PROCESS_ID_SHIFT = 12

    WORKER_ID_MASK = 0x3E0000
    PROCESS_ID_MASK = 0x1F000
    INCREMENT_MASK = 0xFFF

    @classmethod
    def build(
        cls, timestamp: Union[datetime, int, None] = None, worker_id: int = 0,
        process_id: int = 0, increment: int = 0
    ) -> Snowflake:
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        elif isinstance(timestamp, datetime):
            timestamp = timestamp.timestamp()

        timestamp = int((timestamp * 1000) - cls.SNOWFLAKE_EPOCH)

        return cls((timestamp << cls.TIMESTAMP_SHIFT)
                   | (worker_id << cls.WORKER_ID_SHIFT)
                   | (process_id << cls.PROCESS_ID_SHIFT)
                   | increment)

    @overload
    @classmethod
    def try_snowflake(cls, obj: ConvertableToInt) -> Snowflake:
        ...

    @overload
    @classmethod
    def try_snowflake(cls, obj: T) -> T:
        ...

    def try_snowflake(cls, obj: Union[ConvertableToInt, T]) -> Union[Snowflake, T]:
        from ..objects.baseobject import BaseObject

        if isinstance(obj, BaseObject):
            return obj.id

        try:
            return cls(obj)
        except Exception:
            return obj

    @overload
    @classmethod
    def try_snowflake(cls, objs: Iterable[ConvertableToInt]) -> Set[Snowflake]:
        ...

    @overload
    @classmethod
    def try_snowflake(cls, objs: Iterable[T]) -> T:
        ...

    @classmethod
    def try_snowflake_set(cls, objs: Union[ConvertableToInt, T]) -> Union[ConvertableToInt, T]:
        return {cls.try_snowflake(obj) for obj in objs}

    @property
    def timestamp(self) -> int:
        return ((self >> self.TIMESTAMP_SHIFT) + self.SNOWFLAKE_EPOCH) / 1000

    @property
    def time(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp)

    @property
    def worker_id(self) -> int:
        return (self & self.WORKER_ID_MASK) >> self.WORKER_ID_SHIFT

    @property
    def process_id(self) -> int:
        return (self & self.PROCESS_ID_MASK) >> self.PROCESS_ID_SHIFT

    @property
    def increment(self) -> int:
        return self & self.INCREMENT_MASK
