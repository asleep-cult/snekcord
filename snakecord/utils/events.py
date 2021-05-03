from __future__ import annotations

import asyncio
import functools
from numbers import Number
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple
from weakref import WeakSet

__all__ = ('EventNamespace', 'EventWaiter', 'EventDispatcher',
           'EventDefinition')


class EventDefinition:
    """An empty class that merely marks subclasses as being an event."""


class EventNamespace:
    """A class that gathers :class:`EventDefinition` s and stores
    them in :attr:`EventNamespace.__events__` when subclassed.

    Attributes
        __events__: dict[str, EventDefinition]
            The :class:`EventDefinition` s defined in the class.
    """
    __events__: Dict[str, EventDefinition] = {}

    def __init_subclass__(cls):
        cls.__events__ = {}

        for base in cls.__bases__:
            if isinstance(cls, type) and not issubclass(base, EventNamespace):
                continue
            cls.__events__.update(base.__events__)

        for name, attr in cls.__dict__.items():
            if isinstance(attr, type) and issubclass(attr, EventDefinition):
                cls.__events__[name] = attr


class EventWaiter:
    """A class that receives events from an :class:`EventDispatcher`
    if the event passes the filter.

    Attributes
        name: str
            The name of the event that the waiter will receive.

        dispatcher: EventDispatcher
            The :class:`EventDispatcher` that the waiter is
            receiving events from.

        timeout: Optional[Number]
            The maximum amount of time to wait for an event to
            be received, :exc:`asyncio.TimeoutError` is raised
            when this timeout is exceeded.

        filterer: Optional[Callable[..., bool]]
            A callable that determines if the event is wanted,
            e.g.

            .. code-block:: python

                if filterer(event):
                    return event

    .. note::
        This class shouldn't be created directly,
        use :meth:`EventDispatcher.wait` instead.
    """
    def __init__(self, name: str, dispatcher: EventDispatcher,
                 timeout: Optional[Number],
                 filterer: Optional[Callable[..., bool]]) -> None:
        self.name = name
        self.dispatcher = dispatcher
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
        """Closes the waiter and removes it from the
        corresponding :class:`EventDispatcher`, any coroutines
        waiting on it will receive an :exc:`asyncio.CancelledError`.
        """
        if self._future is not None:
            try:
                self._future.cancel()
            except asyncio.InvalidStateError:
                pass
        try:
            self.dispatcher.remove_waiter(self)
        except KeyError:
            pass

    __del__ = close


def ensure_future(coro: Awaitable) -> Optional[asyncio.Future]:
    if hasattr(coro.__class__, '__await__'):
        return asyncio.ensure_future(coro)
    return None


class EventDispatcher:
    """A class dedicated to callbacks, similar to
    Node.js's `EventEmitter`.

    Attributes
        loop: Optional[asyncio.AbstractEventLoop]
            The event loop that is... not used,
            but is useful for subclasses.

    .. note::
        Event names are case insensitive
    """
    events: EventNamespace

    def __init__(self, *,
                 loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        if loop is not None:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()

        self._listeners: Dict[str, List[Callable]] = {}
        self._waiters: Dict[str, WeakSet] = {}
        self._subscribers: List[EventDispatcher] = []

    def register_listener(self, name: str,
                          callback: Callable[..., Any]) -> None:
        """Registers `callback` to be called when an event
        with the same name is dispatched.

        Arguments
            name: str
                The name of the event to listen for.

            callback: Callable[..., Any]
                The callback.
        """
        listeners = self._listeners.setdefault(name.lower(), [])
        listeners.append(callback)

    def remove_listener(self, name: str, callback: Callable[..., Any]) -> None:
        """Unregisters `callback` from being called when an event
        with the same name is dispatched.

        Arguments
            name: str
                The name of the event that was being listened for.

            callback: Callable[..., Any]
                The callback.
        """
        listeners = self._listeners.get(name.lower())
        if listeners is not None:
            listeners.remove(callback)

    def register_waiter(self, name: str, *,
                        timeout: Optional[Number] = None,
                        filterer: Callable[..., Any] = None) -> EventWaiter:
        """Registers a new waiter, see :class:`EventWaiter`
        for information amout arguments.

        Returns
            :class:`EventWaiter`
                The waiter.

        Examples

            .. code-block python::

                async for evnt in dispatcher.wait('hello_world'):
                    print(evnt)

            .. code-block python::

                evnt = await dispatcher.wait('hello_world',
                                             filterer=lambda evnt: 2 + 2 == 4)
        """
        waiters = self._waiters.setdefault(name.lower(), WeakSet())
        waiter = EventWaiter(name, self, timeout, filterer)
        waiters.add(waiter)
        return waiter

    wait = register_waiter

    def remove_waiter(self, waiter: EventWaiter) -> None:
        """Unregisters a waiter, the waiter will stop receiving
        events after this method is called. Consider using
        :meth:`EventWaiter.close` if you'd like to notify
        awaiting coroutines.
        """
        waiters = self._waiters.get(waiter.name.lower())
        if waiters is not None:
            waiters.remove(waiter)

    def run_callbacks(self, name: str, *args: Any) -> None:
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
