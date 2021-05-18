from __future__ import annotations

from datetime import datetime
from numbers import Number
from typing import ClassVar, Final, Optional, Union, SupportsInt

from ..objects.baseobject import BaseSnowflakeObject


_IntConvertable = Union[SupportsInt, str, bytes, bytearray]
SnowflakeConvertable = Union[BaseSnowflakeObject, _IntConvertable]


class Snowflake(int):
    DISCORD_EPOCH: Final[ClassVar[int]]

    TIMESTAMP_SHIFT: Final[ClassVar[int]]
    WORKER_ID_SHIFT: Final[ClassVar[int]]
    PROCESS_ID_SHIFT: Final[ClassVar[int]]

    WORKER_ID_MASK: Final[ClassVar[int]]
    PROCESS_ID_MASK: Final[ClassVar[int]]
    INCREMENT_MASK: Final[ClassVar[int]]

    @classmethod
    def build(cls, timestamp: Optional[Number | datetime] = ...,
              worker_id: int = ..., process_id: int = ...,
              increment: int = ...) -> Snowflake: ...

    @classmethod
    def try_snowflake(cls, obj: SnowflakeConvertable) -> Snowflake: ...

    @property
    def timestamp(self) -> int: ...

    @property
    def time(self) -> datetime: ...

    @property
    def worker_id(self) -> int: ...

    @property
    def process_id(self) -> int: ...

    @property
    def increment(self) -> int: ...
