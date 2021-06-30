import asyncio
import functools
from weakref import WeakSet

__all__ = ('EventWaiter', 'EventDispatcher',)


class EventWaiter:
    def __init__(self, name, *, dispatcher, timeout=None, filter=None):
        self.name = name.lower()
        self.dispatcher = dispatcher
        self.timeout = timeout
        self.filter = filter
        self._queue = asyncio.Queue()

    def _put(self, value):
        if self.filter is not None:
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
    _events_ = None

    def __init__(self, *, loop=None):
        if loop is not None:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()

        self.listeners = {}
        self.waiters = {}
        self.subscribers = []

    def register_listener(self, name, callback):
        listeners = self.listeners.setdefault(name.lower(), [])
        listeners.append(callback)

    def remove_listener(self, name, callback):
        listeners = self.listeners.get(name.lower())
        if listeners is not None:
            listeners.remove(callback)

    def register_waiter(self, *args, **kwargs):
        waiter = EventWaiter(*args, dispatcher=self, **kwargs)
        waiters = self.waiters.setdefault(waiter.name, WeakSet())
        waiters.add(waiter)
        return waiter

    wait = register_waiter

    def remove_waiter(self, waiter) -> None:
        waiters = self.waiters.get(waiter.name.lower())
        if waiters is not None:
            waiters.remove(waiter)

    def run_callbacks(self, name, *args) -> None:
        name = name.lower()
        listeners = self.listeners.get(name)
        waiters = self.waiters.get(name)

        if listeners is not None:
            for listener in tuple(listeners):
                ensure_future(listener(*args))

        if waiters is not None:
            for waiter in tuple(waiters):
                waiter._put(args)

        for subscriber in self.subscribers:
            subscriber.run_callbacks(name, *args)

    async def dispatch(self, name, *args):
        if self._events_ is not None:
            event = self._events_.get(name.lower())
            if event is not None:
                evt = await event(self, *args)
                args = (evt,)

        self.run_callbacks(name, *args)

    def subscribe(self, dispatcher):
        dispatcher.subscribers.append(self)

    def unsubscribe(self, dispatcher):
        dispatcher.subscribers.remove(self)

    def on(self, name=None):
        def wrapped(func):
            self.register_listener(name or func.__name__, func)
            return func
        return wrapped

    def once(self, name=None):
        def wrapped(func):
            @functools.wraps(func)
            def callback(*args, **kwargs):
                self.remove_listener((name or func.__name__).lower(), callback)
                return ensure_future(func(*args, **kwargs))
            return callback
        return wrapped
