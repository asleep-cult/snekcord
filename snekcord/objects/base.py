from __future__ import annotations

from typing import TYPE_CHECKING

from .. import json
from ..exceptions import UnknownObjectError
from ..snowflake import Snowflake

if TYPE_CHECKING:
    from ..clients import Client
    from ..states import BaseCachedState

__all__ = ('SnowflakeObject', 'ObjectWrapper')


class _IDField(json.JSONField):
    def __init__(self) -> None:
        super().__init__('id', repr=True)

    def construct(self, value: str) -> Snowflake:
        return Snowflake(value)

    def deconstruct(self, value: Snowflake) -> str:
        return str(value)


class BaseObject:
    __slots__ = ()

    def __init__(self, *, state: BaseCachedState) -> None:
        self.state = state

    def _get_id(self):
        raise NotImplementedError

    @property
    def client(self) -> Client:
        return self.state.client

    def is_cached(self) -> bool:
        return self._get_id() in self.state.cache.keys()

    async def fetch(self):
        return await self.state.fetch(self._get_id())


class SnowflakeObject(json.JSONObject, BaseObject):
    __slots__ = ('__weakref__', 'state')

    id = _IDField()

    def __init__(self, *, state) -> None:
        super().__init__(state=state)
        self.state.cache[self.id] = self

    def _get_id(self):
        return self.id


class CodeObject(json.JSONObject, BaseObject):
    __slots__ = ('__weakref__', 'state')

    code = json.JSONField('code', repr=True)

    def __init__(self, *, state) -> None:
        super().__init__(state=state)
        self.state.cache[self.code] = self

    def _get_id(self):
        return self.code


class ObjectWrapper(BaseObject):
    __slots__ = ('__weakref__', 'state', 'id')

    def __init__(self, *, state, id) -> None:
        super().__init__(state=state)
        self.set_id(id)

    def __repr__(self) -> str:
        return f'<ObjectWrapper id={self.id}>'

    def _get_id(self):
        return self.id

    def set_id(self, id):
        if id is not None:
            self.id = self.state.unwrap_id(id)
        else:
            self.id = None

    def unwrap(self):
        if self.id is None:
            raise UnknownObjectError(None)

        object = self.state.get(self.id)
        if object is None:
            raise UnknownObjectError(self.id)

        return object
