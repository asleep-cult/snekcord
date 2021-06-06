from weakref import WeakValueDictionary
from collections.abc import MutableMapping
from typing import (Any, Callable, ClassVar, Generic, Iterator,
                    Iterable, Optional, overload, TypeVar)

from ..manager import BaseManager
from ..objects.baseobject import BaseObject
from ..utils import Snowflake, SnowflakeConvertable

KT = TypeVar('KT')
VT = TypeVar('VT')
DT = TypeVar('DT')


class BaseMapping(Generic[KT, VT]):
    def __iter__(self) -> Iterator[VT]: ...

    def __reversed__(self) -> reversed[VT]: ...

    @classmethod
    def for_type(cls, klass: type[MutableMapping[KT, VT]]
                 ) -> type[BaseMapping[KT, VT]]: ...


class BaseSnowflakeMapping(BaseMapping[Snowflake, VT]):
    def __getitem__(self, key: SnowflakeConvertable) -> VT: ...

    def __setitem__(self, key: SnowflakeConvertable,
                    value: VT) -> None: ...

    def get(self, key: SnowflakeConvertable,
            default: DT) -> SnowflakeConvertable | DT: ...

    @overload
    def pop(self, key: SnowflakeConvertable) -> VT: ...

    @overload
    def pop(self, key: SnowflakeConvertable, default: DT) -> VT | DT: ...


class Mapping(BaseMapping[KT, VT], dict[KT, VT]):
    ...


class SnowflakeMapping(BaseSnowflakeMapping[VT], dict[Snowflake, VT]):
    ...


class WeakValueMapping(BaseMapping[KT, VT], WeakValueDictionary[KT, VT]):
    ...


class WeakValueSnowflakeMapping(BaseSnowflakeMapping[VT],
                                WeakValueDictionary[Snowflake, VT]):
    ...


class _StateCommon(Generic[KT]):
    def __contains__(self, key: BaseObject[KT]) -> bool: ...

    def find(self, func: Callable[[BaseObject[KT]], bool]
             ) -> Optional[BaseObject[KT]]: ...


class BaseState(_StateCommon[KT]):
    __container__: ClassVar[type[Mapping[KT, BaseObject[KT]]]]
    __recycled_container__: ClassVar[type[Mapping[KT, BaseObject[KT]]]]
    __maxsize__: ClassVar[int]
    __replace__: ClassVar[bool]
    _items: Mapping[KT, BaseObject[KT]]
    _recycle_bin: Mapping[KT, BaseObject[KT]]
    manager: BaseManager

    def __init__(self, *, manager: BaseManager) -> None: ...

    @classmethod
    def set_maxsize(cls, maxsize: int) -> None: ...

    @classmethod
    def get_maxsize(cls) -> int: ...

    @classmethod
    def set_replace(cls, replace: bool) -> None: ...

    def __repr__(self) -> str: ...

    def __len__(self) -> int: ...

    def __reversed__(self) -> Iterable[BaseObject[KT]]: ...

    def __iter__(self) -> Iterator[BaseObject[KT]]: ...

    def set(self, key: KT, value: BaseObject[KT]) -> bool: ...

    __setitem__ = set

    def __getitem__(self, key: KT) -> BaseObject[KT]: ...

    def keys(self) -> Iterable[KT]: ...

    def values(self) -> Iterable[BaseObject[KT]]: ...

    def recycle(self) -> None: ...

    @overload
    def unrecycle(self, key: KT) -> BaseObject[KT]: ...

    @overload
    def unrecycle(self, key: KT, default: DT) -> BaseObject[KT] | DT: ...

    def get(self, key: KT, default: DT = ...) -> BaseObject[KT] | DT: ...

    @overload
    def pop(self, key: KT) -> BaseObject[KT]: ...

    @overload
    def pop(self, key: KT, default: DT) -> BaseObject[KT] | DT: ...

    def popitem(self) -> tuple[KT, BaseObject[KT]]: ...

    def append(self, data: dict[str, Any]) -> BaseObject[KT]: ...

    def extend(self, data: Iterable[dict[str, Any]]) -> list[BaseObject[KT]]: ...


BaseSnowflakeState = BaseState[Snowflake]


class BaseSubState(Generic[KT]):
    superstate: BaseState[KT]
    _keys: set[KT]

    def add_key(self, key: KT) -> None: ...

    def set_keys(self, keys: Iterable[KT]) -> None: ...

    def remove_key(self, key: KT) -> None: ...

    def __key_for__(self, item: BaseObject[KT]) -> KT: ...

    def __repr__(self) -> str: ...

    def __len__(self) -> int: ...

    def __iter__(self) -> Iterator[BaseObject[KT]]: ...

    def __reversed__(self) -> Iterator[BaseObject[KT]]: ...

    def __getitem__(self, key: KT) -> BaseObject[KT]: ...

    def get(self, key: KT, default: DT) -> BaseObject[KT] | DT: ...


BaseSnowflakeSubState = BaseSubState[Snowflake]
