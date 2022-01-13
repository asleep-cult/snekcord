import enum
import inspect
from collections import defaultdict
from typing import TYPE_CHECKING

from ..collection import Collection
from ..objects import ObjectWrapper

if TYPE_CHECKING:
    from ..json import JSONData
    from ..clients.client import Client

__all__ = ('BaseState',)


class StateCacheMixin:
    def __init__(self):
        self.cache = Collection()

    def unwrap_id(self, object):
        raise NotImplementedError

    def __contains__(self, object) -> bool:
        return self.unwrap_id(object) in self.cache.keys()

    def __iter__(self):
        return iter(self.cache)

    def get(self, object):
        return self.cache.get(self.unwrap_id(object))

    def pop(self, object):
        return self.cache.pop(self.unwrap_id(object))

    async def upsert(self, data):
        raise NotImplementedError


class BaseState:
    def __init__(self, *, client: Client) -> None:
        self.client = client
        self._callbacks = defaultdict(list)
        self._waiters = defaultdict(list)

        self._dispatchers = {}
        for name, func in inspect.getmembers(self):
            if name.startswith('dispatch_'):
                self._dispatchers[name[9:].upper()] = func

    def _get_client(self) -> Client:
        return self.client

    def unwrap_id(self, object):
        raise NotImplementedError

    def wrap_id(self, object):
        return ObjectWrapper(state=self, id=object)

    def get_events(self) -> enum.Enum:
        raise NotImplementedError

    def cast_event(self, event: str) -> enum.Enum:
        return self.get_events()(event)

    def on(self, event: str):
        event = self.cast_event()

        def decorator(func):
            self._callbacks[event].append(func)

        return decorator

    async def dispatch(self, event: str, payload: JSONData) -> None:
        event = self.cast_event(event)

        dispatcher = self._dispatchers[event]
        ret = await dispatcher(payload)

        for callback in self._callbacks[event]:
            self.client.loop.create_task(callback(ret))
