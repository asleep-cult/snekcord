from __future__ import annotations

import asyncio
import functools
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Type
from weakref import WeakSet


class EventNamespaceMeta(type):
    def __new__(cls, name, bases, attrs):
        events = attrs.setdefault('__events__', {})
        for base in bases:
            if isinstance(base, EventNamespaceMeta):
                events.update(base.__events__)

        return super().__new__(cls, name, bases, attrs)


class EventNamespace(metaclass=EventNamespaceMeta):
    __events__: Dict[str, type]

class eventdef(type):
    def __set_name__(cls, owner, name):
        assert isinstance(owner, EventNamespaceMeta)
        owner.__events__[name] = cls
        setattr(owner, name, cls)


class EventWaiter:
    def __init__(self, name: str, pusher: EventDispatcher,
                 timeout: Optional[float],
                 filterer: Optional[Callable[..., bool]]) -> None:
        self.name = name
        self.pusher = pusher
        self.timeout = timeout
        self.filterer = filterer
        self._future: Optional[asyncio.Future] = None
        self._queue: asyncio.Queue[Tuple[Any]] = asyncio.Queue()

    def _put(self, value: Tuple[Any]) -> None:
        if self.filterer is None or self.filterer(*value):
            self._queue.put_nowait(value)

    async def _get(self) -> Any:
        self._future = asyncio.ensure_future(
            asyncio.wait_for(self._queue.get(), timeout=self.timeout))
        # XXX: this is probably creates like 4 wrapped futures...
        value = await self._future
        if len(value) == 1:
            value, = value

        return value

    def __aiter__(self) -> EventWaiter:
        return self

    async def __anext__(self) -> Any:
        return await self._get()

    async def __await__impl(self) -> None:
        try:
            return await self._get()
        finally:
            self.close()

    def __await__(self):
        return self.__await__impl().__await__()

    def close(self) -> None:
        if self._future is not None:
            try:
                self._future.cancel()
            except asyncio.InvalidStateError:
                pass
        try:
            self.pusher.remove_waiter(self)
        except KeyError:
            pass

    __del__ = close


def ensure_future(coro: Awaitable) -> Optional[asyncio.Future]:
    if hasattr(coro.__class__, '__await__'):
        return asyncio.ensure_future(coro)
    return None


class EventDispatcher:
    def __init__(self, *,
                 loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        if loop is not None:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()

        self._listeners: Dict[str, List[Callable]] = {}
        self._waiters: Dict[str, WeakSet] = {}
        self._subscribers: List[EventDispatcher] = []

    def register_listener(self, name: str, func: Callable[..., Any]) -> None:
        listeners = self._listeners.setdefault(name.lower(), [])
        listeners.append(func)

    def remove_listener(self, name: str, func: Callable[..., Any]) -> None:
        listeners = self._listeners.get(name.lower())
        if listeners is not None:
            listeners.remove(func)

    def register_waiter(self, name: str, *,
                        timeout: Optional[float] = None,
                        filterer: Optional[Callable[..., bool]] = None) -> EventWaiter:
        waiters = self._waiters.setdefault(name.lower(), WeakSet())
        waiter = EventWaiter(name, self, timeout, filterer)
        waiters.add(waiter)
        return waiter

    wait = register_waiter

    def remove_waiter(self, waiter: EventWaiter) -> None:
        waiters = self._waiters.get(waiter.name.lower())
        if waiters is not None:
            waiters.remove(waiter)

    def run_callbacks(self, name, *args: Any) -> None:
        name = name.lower()
        listeners = self._listeners.get(name)
        waiters = self._waiters.get(name)

        if listeners is not None:
            for listener in listeners:
                ensure_future(listener(*args))

        if waiters is not None:
            for waiter in waiters:
                waiter._put(*args)

        for subscriber in self._subscribers:
            subscriber.run_callbacks(name, *args)

    def dispatch(self, name: str, *args) -> None:
        event = self.events.__events__.get(name.lower())

        if event is not None:
            args = (event(self, *args),)

        self.run_callbacks(name, *args)

    def subscribe(self, pusher: EventDispatcher):
        pusher._subscribers.append(self)

    def unsubscribe(self, pusher: EventDispatcher):
        pusher._subscribers.remove(self)

    def on(self, name: Optional[str] = None):
        def wrapped(func: Callable[..., Any]):
            self.register_listener(name or func.__name__, func)
            return func
        return wrapped

    def once(self, name: Optional[str] = None):
        def wrapped(func):
            nonlocal name
            name = (name or func.__name__).lower()

            @functools.wraps(func)
            def callback(*args):
                ensure_future(func, *args)
                self.remove_listener(name, callback)

            self.remove_listener(name, callback)

            return func
        return wrapped
