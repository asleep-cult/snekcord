from __future__ import annotations

import typing as t

from ..typedefs import Json

__all__ = ('JsonObject', 'JsonField', 'JsonArray')

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
