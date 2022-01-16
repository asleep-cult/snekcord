from __future__ import annotations

import asyncio
import enum
from collections import defaultdict
from typing import TYPE_CHECKING

from ..collection import (
    Collection,
    WeakCollection,
)
from ..objects import ObjectWrapper

if TYPE_CHECKING:
    from ..events import BaseEvent
    from ..intents import WebSocketIntents
    from ..json import JSONData
    from ..websockets import ShardWebSocket
    from ..clients.client import Client

__all__ = ('BaseState',)


class BaseState:
    def __init__(self, *, client: Client) -> None:
        self.client = client
        self._callbacks = defaultdict(list)
        self._waiters = defaultdict(list)

    @classmethod
    def unwrap_id(cls, object):
        raise NotImplementedError

    def get_events(self) -> type[enum.Enum]:
        raise NotImplementedError

    def cast_event(self, event: str) -> enum.Enum:
        return self.get_events()(event)

    def get_intents(self) -> WebSocketIntents:
        raise NotImplementedError

    def listen(self):
        self.client.enable_events(self)

    def on(self, event: str):
        event = self.cast_event(event)

        def decorator(func):
            if not asyncio.iscoroutinefunction(func):
                raise TypeError('The callback should be a coroutine function.')

            self._callbacks[event].append(func)

        return decorator

    async def process_event(
        self, event: str, shard: ShardWebSocket, payload: JSONData
    ) -> BaseEvent:
        raise NotImplementedError

    async def dispatch(self, event: str, shard: ShardWebSocket, payload: JSONData) -> None:
        ret = await self.process_event(event, shard, payload)

        for callback in self._callbacks[event]:
            self.client.loop.create_task(callback(ret))


class BaseCachedState(BaseState):
    def __init__(self, *, client: Client) -> None:
        super().__init__(client=client)
        self.cache = Collection()

    def wrap_id(self, object):
        return ObjectWrapper(state=self, id=object)

    def __contains__(self, object) -> bool:
        return self.unwrap_id(object) in self.cache.keys()

    def __iter__(self):
        return iter(self.cache)

    def get(self, object):
        return self.cache.get(self.unwrap_id(object))

    def pop(self, object):
        return self.cache.pop(self.unwrap_id(object), None)

    async def upsert(self, data):
        raise NotImplementedError


class BaseSubsidiaryState:
    def __init__(self, *, superstate: BaseState) -> None:
        self.superstate = superstate

        if isinstance(superstate, BaseCachedState):
            self.cache = WeakCollection()
        else:
            self.cache = Collection()

    @property
    def client(self) -> Client:
        return self.superstate.client

    def unwrap_id(self, object):
        return self.superstate.unwrap_id(object)

    def wrap_id(self, object):
        if isinstance(self.superstate, BaseCachedState):
            return self.superstate.wrap_id(object)

        return ObjectWrapper(state=self, id=object)

    def __contains__(self, object) -> bool:
        return self.unwrap_id(object) in self.cache.keys()

    def __iter__(self):
        return iter(self.cache)

    def get(self, object):
        return self.cache.get(self.unwrap_id(object))

    def pop(self, object):
        return self.cache.pop(self.unwrap_id(object), None)

    async def upsert(self, data):
        if not isinstance(self.superstate, BaseCachedState):
            raise NotImplementedError(
                'Subsidiary state with non-cached superstate must implement upsert'
            )

        object = await self.superstate.upsert(data)
        self.cache[self.unwrap_id(object)] = object

        return object
