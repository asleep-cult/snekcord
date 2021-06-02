import asyncio
import functools
from weakref import WeakSet

__all__ = ('EventWaiter', 'EventDispatcher',)


class EventWaiter:
    def __init__(self, name, *, dispatcher, timeout=None,
                 filterer=None):
        self.name = name.lower()
        self.dispatcher = dispatcher
        self.timeout = timeout
        self.filterer = filterer
        self._queue = asyncio.Queue()

    def _put(self, value):
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


def ensure_future(coro):
    if hasattr(coro.__class__, '__await__'):
        return asyncio.ensure_future(coro)
    return None


class EventDispatcher:
    __events__ = None

    def __init__(self, *, loop=None):
        if loop is not None:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()

        self._listeners = {}
        self._waiters = {}
        self._subscribers = []

    def register_listener(self, name, callback):
        listeners = self._listeners.setdefault(name.lower(), [])
        listeners.append(callback)

    def remove_listener(self, name, callback):
        listeners = self._listeners.get(name.lower())
        if listeners is not None:
            listeners.remove(callback)

    def register_waiter(self, *args, **kwargs):
        waiter = EventWaiter(*args, dispatcher=self, **kwargs)
        waiters = self._waiters.setdefault(waiter.name, WeakSet())
        waiters.add(waiter)
        return waiter

    wait = register_waiter

    def remove_waiter(self, waiter):
        waiters = self._waiters.get(waiter.name.lower())
        if waiters is not None:
            waiters.remove(waiter)

    def run_callbacks(self, name, *args):
        name = name.lower()
        listeners = self._listeners.get(name)
        waiters = self._waiters.get(name)

        if listeners is not None:
            for listener in listeners:
                ensure_future(listener(*args))

        if waiters is not None:
            for waiter in waiters:
                waiter._put(args)

        for subscriber in self._subscribers:
            subscriber.run_callbacks(name, *args)

    def dispatch(self, name, *args):
        if self.__events__ is not None:
            event = self.__events__.get(name.lower())
            if event is not None:
                args = (event(*args),)

        self.run_callbacks(name, *args)

    def subscribe(self, dispatcher):
        dispatcher._subscribers.append(self)

    def unsubscribe(self, dispatcher):
        dispatcher._subscribers.remove(self)

    def on(self, name=None):
        def wrapped(func):
            self.register_listener(name or func.__name__, func)
            return func
        return wrapped

    def once(self, name=None):
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
