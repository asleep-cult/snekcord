from __future__ import annotations

from typing import Any, Callable, Final, Optional


class JsonTemplate:
    fields: dict[str, JsonField]

    def __init__(self, *, __extends__: tuple[JsonField] = ...,
                 **fields: JsonField) -> None: ...

    def update(self, obj: Any, data: dict[str, Any],
               set_default: bool = ...) -> None: ...

    def to_dict(self, obj: Any) -> dict[str, Any]: ...

    def marshal(self, obj: Any, *args: Any, **kwargs: Any) -> str: ...
    # TODO: *args: json.dumps.args, **kwargs: json.dumps.kwargs ?

    def default_object(self) -> JsonObjectMeta: ...


class JsonField:
    key: str
    object: Optional[JsonObjectMeta]
    omitempty: bool
    _default: Optional[Callable[[Any], Any]]
    _unmarshal: Optional[Callable[[Any], Any]]
    _marshal: Optional[Callable[[Any], Any]]

    def __init__(self, key: str,
                 unmarshal: Optional[Callable[[Any], Any]] = ...,
                 marshal: Optional[Callable[[Any], Any]] = ...,
                 object: Optional[JsonObjectMeta] = ...,
                 default: Optional[Callable[[Any], Any]] = ...,
                 omitempty: bool = ...) -> None: ...

    def unmarshal(self, value: Any) -> Any: ...

    def marshal(self, value: Any) -> Any: ...

    def default(self) -> Any: ...


class JsonArray(JsonField):
    def unmarshal(self, value: list) -> list: ...

    def marshal(self, value: list) -> list: ...


class JsonObjectMeta(type):
    __slots__: Final[set[str]]
    __template__: Final[JsonTemplate]


class JsonObject(metaclass=JsonObjectMeta):
    @classmethod
    def unmarshal(cls, data, *args: Any, **kwargs: Any) -> JsonObject: ...

    def update(self, *args: Any, **kwargs: Any) -> None: ...

    def to_dict(self, *args: Any, **kwargs: Any) -> dict[str, Any]: ...

    def marshal(self, *args: Any, **kwargs: Any) -> str: ...
