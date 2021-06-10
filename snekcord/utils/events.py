from __future__ import annotations

import asyncio
import functools
import typing as t
from weakref import WeakSet

if t.TYPE_CHECKING:
    from ..typing import AnyCallable, AnyCoroCallable, ParamSpec

    P = ParamSpec('P')

__all__ = ('EventWaiter', 'EventDispatcher',)

T = t.TypeVar('T')


class EventWaiter:
    name: str
    dispatcher: EventDispatcher
    timeout: float | None
    filterer: AnyCallable | None
    _queue: asyncio.Queue[t.Any]

    def __init__(self, name: str, *, dispatcher: EventDispatcher,
                 timeout: float | None = None,
                 filterer: t.Callable[..., t.Any] | None = None) -> None:
        self.name = name.lower()
        self.dispatcher = dispatcher
        self.timeout = timeout
        self.filterer = filterer
        self._queue = asyncio.Queue()

    def _put(self, value: tuple[t.Any, ...]) -> None:
        if self.filterer is not None:
            if not self.filterer(*value):
                return

        self._queue.put_nowait(value)

    async def _get(self):
        value = await asyncio.wait_for(self._queue.get(), timeout=self.timeout)
        if len(value) == 1:
            value, = value

        return value

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self._get()

    async def __await__impl(self):
        try:
            return await self._get()
        finally:
            self.close()

    def __await__(self):
        return self.__await__impl().__await__()

    def close(self):
        try:
            self.dispatcher.remove_waiter(self)
        except KeyError:
            pass

    __del__ = close


def ensure_future(coro: t.Any) -> asyncio.Future[t.Any] | None:
    if hasattr(coro.__class__, '__await__'):
        return asyncio.ensure_future(coro)
    return None


class EventDispatcher:
    __events__: t.ClassVar[dict[str, AnyCoroCallable] | None] = None
    loop: asyncio.AbstractEventLoop
    listeners: dict[str, list[AnyCallable]]
    waiters: dict[str, WeakSet[EventWaiter]]
    subscribers: list[EventDispatcher]

    def __init__(self, *,
                 loop: asyncio.AbstractEventLoop | None = None) -> None:
        if loop is not None:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()

        self.listeners = {}
        self.waiters = {}
        self.subscribers = []

    def register_listener(self, name: str, callback: AnyCallable) -> None:
        listeners = self.listeners.setdefault(name.lower(), [])
        listeners.append(callback)

    def remove_listener(self, name: str, callback: AnyCallable) -> None:
        listeners = self.listeners.get(name.lower())
        if listeners is not None:
            listeners.remove(callback)

    def register_waiter(self, *args: t.Any, **kwargs: t.Any) -> EventWaiter:
        waiter = EventWaiter(*args, dispatcher=self, **kwargs)
        waiters = self.waiters.setdefault(waiter.name, WeakSet())
        waiters.add(waiter)
        return waiter

    wait = register_waiter

    def remove_waiter(self, waiter: EventWaiter) -> None:
        waiters = self.waiters.get(waiter.name.lower())
        if waiters is not None:
            waiters.remove(waiter)

    def run_callbacks(self, name: str, *args: t.Any) -> None:
        name = name.lower()
        listeners = self.listeners.get(name)
        waiters = self.waiters.get(name)

        if listeners is not None:
            for listener in tuple(listeners):
                ensure_future(listener(*args))

        if waiters is not None:
            for waiter in tuple(waiters):
                waiter._put(args)  # type: ignore

        for subscriber in self.subscribers:
            subscriber.run_callbacks(name, *args)

    async def dispatch(self, name: str, *args: t.Any):
        if self.__events__ is not None:
            event = self.__events__.get(name.lower())
            if event is not None:
                args = (await event(self, *args),)

        self.run_callbacks(name, *args)

    def subscribe(self, dispatcher: EventDispatcher) -> None:
        dispatcher.subscribers.append(self)

    def unsubscribe(self, dispatcher: EventDispatcher) -> None:
        dispatcher.subscribers.remove(self)

    def on(
        self, name: t.Optional[str] = None
    ) -> t.Callable[[t.Callable[P, T]], t.Callable[P, T]]:
        def wrapped(func: t.Callable[P, T]) -> t.Callable[P, T]:
            self.register_listener(name or func.__name__, func)
            return func
        return wrapped

    def once(
        self, name: t.Optional[str] = None
    ) -> t.Callable[[t.Callable[P, t.Awaitable[t.Any]]], t.Callable[P, None]]:
        def wrapped(
            func: t.Callable[P, t.Awaitable[t.Any]]
        ) -> t.Callable[P, None]:
            event_name = (name or func.__name__).lower()

            @functools.wraps(func)
            def callback(*args: P.args, **kwargs: P.kwargs) -> None:
                ensure_future(func(*args, **kwargs))
                self.remove_listener(event_name, callback)

            return callback
        return wrapped
