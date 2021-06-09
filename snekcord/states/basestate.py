from __future__ import annotations

import weakref
from typing import (Any, Callable, ClassVar, Generic, Iterator,
                    Iterable, List, MutableMapping, Optional,
                    Set, TYPE_CHECKING, Tuple, Type, TypeVar, Union, overload)

from ..utils import undefined

__all__ = ('BaseState', 'BaseSubState')

if TYPE_CHECKING:
    from ..clients import Client
    from ..objects.baseobject import BaseObject

KT = TypeVar('KT')
VT_co = TypeVar('VT_co', covariant=True)
DT = TypeVar('DT')
OT_co = TypeVar('OT_co', bound='BaseObject', covariant=True)


class _StateCommon(Generic[KT, VT_co]):
    def first(
        self, func: Optional[Callable[[VT_co], Any]] = None
    ) -> Optional[VT_co]:
        for value in self:
            if func is None or func(value):
                return value
        return None

    def __iter__(self) -> Iterator[VT_co]:
        raise NotImplementedError


class BaseState(_StateCommon[KT, OT_co]):
    __key_transformer__: Optional[Callable[[KT], Any]] = None
    __mapping__: Type[MutableMapping[KT, OT_co]] = dict
    __recycle_enabled__: bool = True
    __recycled_mapping__: ClassVar[
        Type[weakref.WeakValueDictionary[KT, OT_co]]
    ]
    __recycled_mapping__ = weakref.WeakValueDictionary

    client: Client
    mapping: weakref.WeakValueDictionary[KT, OT_co]
    recycle_bin: Optional[MutableMapping[KT, OT_co]]

    def __init__(self, *, client: Client) -> None:
        self.client = client
        self.mapping = self.__mapping__()  # type: ignore
        if self.__recycle_enabled__:
            self.recycle_bin = self.__recycled_mapping__()
        else:
            self.recycle_bin = None

    def transform_key(self, key: Any) -> KT:
        if self.__key_transformer__ is None:
            return key
        return self.__key_transformer__(key)

    def __len__(self) -> int:
        return self.__mapping__.__len__(self.mapping)

    def __iter__(self) -> Iterator[OT_co]:
        return iter(self.values())

    def __reversed__(self) -> Iterable[OT_co]:
        return reversed(list(self.values()))

    def __contains__(self, key: KT) -> bool:
        return self.__mapping__.__contains__(
            self.mapping, self.transform_key(key))

    def __getitem__(self, key: KT) -> OT_co:
        return self.__mapping__.__getitem__(
            self.mapping, self.transform_key(key))

    def __setitem__(self, key: KT, value: OT_co) -> None:  # type: ignore
        return self.__mapping__.__setitem__(
            self.mapping, self.transform_key(key), value)

    def __delitem__(self, key: KT):
        return self.__mapping__.__delitem__(
            self.mapping, self.transform_key(key))

    def __repr__(self) -> str:
        attrs: List[Tuple[str, int]] = [('length', len(self))]

        if self.__recycle_enabled__:
            attrs.append(('recycled', len(self.recycle_bin)))  # type: ignore

        formatted = ', '.join(f'{name}={value}' for name, value in attrs)
        return f'{self.__class__.__name__}({formatted})'

    def keys(self) -> Iterable[KT]:
        return self.__mapping__.keys(self.mapping)

    def values(self) -> Iterable[OT_co]:
        return self.__mapping__.values(self.mapping)

    def items(self) -> Iterable[Tuple[KT, OT_co]]:
        return self.__mapping__.items(self.mapping)

    @overload
    def get(self, key: KT) -> Optional[OT_co]:
        ...

    @overload
    def get(self, key: KT, default: DT) -> Union[OT_co, DT]:
        ...

    def get(self, key: KT, default: DT = None) -> Union[DT, OT_co]:
        key = self.transform_key(key)
        value = self.mapping.get(key)
        if value is None:
            if self.recycle_bin is not None:
                value = self.recycle_bin.get(key, default)
            else:
                value = default
        return value

    @overload
    def pop(self, key: KT) -> OT_co:
        ...

    @overload
    def pop(self, key: KT, default: DT) -> Union[OT_co, DT]:
        ...

    def pop(self, key: KT, default: Any = undefined) -> Union[OT_co, Any]:
        key = self.transform_key(key)
        try:
            return self.__mapping__.pop(self.mapping, key)
        except KeyError:
            try:
                if self.recycle_bin is not None:
                    return self.recycle_bin.pop(key)
                raise
            except KeyError:
                if default is not undefined:
                    return default
                raise

    def popitem(self) -> Tuple[KT, OT_co]:
        return self.__mapping__.popitem(self.mapping)

    def clear(self) -> None:
        return self.__mapping__.clear(self.mapping)

    def upsert(self, *args: Any, **kwargs: Any) -> OT_co:
        raise NotImplementedError

    def upsert_many(
        self, values: Iterable[Any], *args: Any, **kwargs: Any
    ) -> Set[OT_co]:
        return {self.upsert(value, *args, **kwargs) for value in values}

    def upsert_replace(self, *args: Any, **kwargs: Any):
        values = self.upsert_many(*args, **kwargs)

        for value in set(self):
            if value not in values:
                value._delete()  # type: ignore

        return values

    def recycle(self, key: KT, value: OT_co) -> None:  # type: ignore
        if self.__recycle_enabled__ and self.recycle_bin:
            return self.recycle_bin.__setitem__(
                self.transform_key(key),
                value)

    def unrecycle(self, key: KT, *args: Any, **kwargs: Any) -> None:
        if self.__recycle_enabled__:
            return self.__recycled_mapping__.pop(
                self.recycle_bin, self.transform_key(key),
                *args, **kwargs)  # type: ignore

    async def fetch(self, *args: Any, **kwargs: Any) -> OT_co:
        raise NotImplementedError


class BaseSubState(_StateCommon[KT, OT_co]):
    if TYPE_CHECKING:
        superstate: BaseState[KT, OT_co]
        _keys: Set[KT]

    def __init__(self, *, superstate: BaseState[KT, OT_co]):
        self.superstate = superstate
        self._keys = set()

    def __len__(self) -> int:
        return len(self._keys)

    def __iter__(self) -> Iterator[OT_co]:
        for key in self._keys:
            try:
                yield self.superstate[key]
            except KeyError:
                continue

    def __reversed__(self) -> Iterator[OT_co]:
        for key in reversed(list(self._keys)):
            try:
                yield self.superstate[key]
            except KeyError:
                continue

    def __contains__(self, key: KT) -> bool:
        return self.superstate.transform_key(key) in self._keys

    def __getitem__(self, key: KT) -> OT_co:
        if self.superstate.transform_key(key) not in self._keys:
            raise KeyError(key)
        return self.superstate[key]

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}(length={len(self)}, '
                f'superstate={self.superstate!r})')

    def set_keys(self, keys: Iterable[KT]) -> None:
        self._keys = {self.superstate.transform_key(key) for key in keys}

    def add_key(self, key: KT) -> None:
        self._keys.add(self.superstate.transform_key(key))

    def extend_keys(self, keys: Iterable[KT]) -> None:
        self._keys.update({self.superstate.transform_key(key) for key in keys})

    def remove_key(self, key: KT) -> None:
        self._keys.remove(self.superstate.transform_key(key))

    def clear_keys(self) -> None:
        self._keys.clear()

    def keys(self) -> Set[KT]:
        return self._keys

    def values(self) -> Iterator[OT_co]:
        return iter(self)

    def items(self) -> Iterator[Tuple[KT, OT_co]]:
        for key in self._keys:
            yield key, self.superstate[key]

    def get(self, key: KT, default: DT = None) -> Union[OT_co, DT]:
        if self.superstate.transform_key(key) not in self._keys:
            return default
        return self.superstate.get(key, default)
