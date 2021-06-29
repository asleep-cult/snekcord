from __future__ import annotations

import typing as t

from ..typedefs import AnyCallable, Json

T = t.TypeVar('T')

__all__ = ('JsonTemplate', 'JsonField', 'JsonArray', 'JsonObject')


class JsonTemplate:
    local_fields: dict[str, JsonField]
    fields: dict[str, JsonField]

    def __init__(self, __extends__: tuple[JsonTemplate, ...] = ...,
                 **fields: JsonField) -> None: ...

    def update(self, obj: JsonObject, data: Json, *,
               set_defaults: bool = ...) -> None: ...

    def to_dict(self, obj: JsonObject) -> Json: ...

    def marshal(self, obj: JsonObject, *args: t.Any,
                **kwargs: t.Any) -> str: ...

    def default_type(self, name: str = ...) -> type[JsonObject]: ...


class JsonField:
    key: str
    object: type[JsonObject] | None

    def __init__(self, key: str, marshal: AnyCallable | None = ...,
                 object: type[JsonObject] | None = ...,
                 default: t.Any = ...) -> None: ...

    def unmarshal(self, value: t.Any) -> t.Any: ...

    def marshal(self, value: t.Any) -> t.Any: ...

    def default(self) -> t.Any: ...


class JsonArray(JsonField):
    def unmarshal(self, value: list[t.Any]) -> list[t.Any]: ...

    def marshal(self, value: list[t.Any]) -> list[t.Any]: ...


class JsonObjectMeta(type):
    def __new__(cls, name: str, bases: tuple[type, ...],
                attrs: dict[str, t.Any],
                template: JsonTemplate | None = ...) -> None: ...


class JsonObject(metaclass=JsonObjectMeta):
    __template__: t.ClassVar[JsonTemplate | None]

    __fields__: set[str]

    @classmethod
    def unmarshal(cls: type[T], data: Json | t.ByteString | None = ...,
                  *args: t.Any, **kwargs: t.Any) -> T: ...

    def update(self, *args: t.Any, **kwargs: t.Any) -> None: ...

    def to_dict(self) -> Json: ...

    def marshal(self, *args: t.Any, **kwargs: t.Any) -> str: ...
