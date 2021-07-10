from __future__ import annotations

import typing as t
from datetime import datetime

from .typedefs import Json, SnowflakeConvertible

__all__ = ('JsonObject', 'JsonField', 'JsonArray', 'Snowflake', 'undefined')

T = t.TypeVar('T')
FT = t.TypeVar('FT')


class JsonObject:
    _json_data_: Json

    @classmethod
    def unmarshal(cls: type[T], data: Json | None = ..., **kwargs: t.Any) -> T: ...

    def update(self, data: Json) -> None: ...

    def to_dict(self) -> Json: ...

    def marshal(self, *args: t.Any, **kwargs: t.Any) -> str: ...


class JsonField(t.Generic[FT]):
    def __init__(self, key: str, unmarshaler: t.Callable[[t.Any], FT] | None = ...,
                 object: type[JsonObject] | None = ...,
                 default: t.Callable[[], FT] | FT | None = ...) -> None: ...

    def __set_name__(self, instance: JsonObject, name: str) -> None: ...

    @t.overload
    def __get__(self, instance: None, owner: type[JsonObject]) -> JsonField[FT]: ...

    @t.overload
    def __get__(self, instance: JsonObject, owner: type[JsonObject]) -> FT | None: ...

    def __set__(self, instance: JsonObject, value: t.Any) -> t.NoReturn: ...

    def __delete__(self, instance: JsonObject) -> t.NoReturn: ...

    def _unmsrshal_(self, value: t.Any) -> FT: ...

    def unmarshaler(self, func: T) -> T: ...


class JsonArray(JsonField[FT]):
    @t.overload
    def __get__(self, instance: None, owner: type[JsonObject]) -> JsonField[FT]: ...

    @t.overload
    def __get__(self, instance: JsonObject, owner: type[JsonObject]) -> list[FT] | None: ...

    def _unmsrshal_(self, value: list[t.Any]) -> list[FT]: ...


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
    def try_snowflake_many(cls, objs: t.Iterable[SnowflakeConvertible]) -> tuple[Snowflake]: ...

    @property
    def timestamp(self) -> float: ...

    @property
    def worker_id(self) -> int: ...

    @property
    def process_id(self) -> int: ...

    @property
    def increment(self) -> int: ...

    @property
    def to_datetime(self) -> datetime: ...


class Undefined:
    def __bool__(self) -> t.Literal[False]: ...


undefined: Undefined
