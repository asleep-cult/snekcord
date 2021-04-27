import asyncio
import weakref
from typing import Any, Callable, Optional

class EventWaiter:
    def __init__(self, pusher: 'EventPusher', name: str, timeout: Optional[float], filter: Optional[Callable[..., bool]]):
        self.pusher = pusher
        self.name = name
        self.timeout = timeout
        self.filter = filter
        self._queue = asyncio.Queue()

    async def _wait_filtered(self):
        while True:
            ret = await self._queue.get()

            if self.filter is not None:
                if not self.filter(*ret):
                    continue

            if len(ret) == 1:
                ret = ret[0]

            return ret

    async def _do_wait(self):
        return await asyncio.wait_for(self._wait_filtered(), timeout=self.timeout)

    def __aiter__(self):
        return self

    __anext__ = _do_wait

    async def __await__impl(self):
        try:
            ret = await self._do_wait()
        finally:
            self._cleanup()
        return ret

    def __await__(self):
        return self.__await__impl().__await__()

    def _cleanup(self):
        try:
            self.pusher.remove_waiter(self)
        except KeyError:
            pass

    __del__ = _cleanup


def run_coroutine(coro: Any, loop: asyncio.AbstractEventLoop) -> None:
    if asyncio.iscoroutine(coro):
        loop.create_task(coro)


class EventPusher:
    handlers = ()

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self._handlers = {handler.name: handler for handler in self.handlers}
        self._listeners = {}
        self._waiters = {}
        self._subscribers = []

    def register_listener(self, name: str, func: Callable[..., Any]):
        name = name.lower()
        listeners = self._listeners.get(name)

        if listeners is None:
            listeners = []
            self._listeners[name] = listeners

        listeners.append(func)

    def remove_listener(self, name: str, func: Callable[..., Any]):
        name = name.lower()
        listeners = self._listeners.get(name)

        if listeners is None:
            return

        listeners.remove(func)

    def register_waiter(self, name: str, *, timeout: Optional[float] = None, filter: Optional[Callable[..., Any]] = None):
        name = name.lower()
        waiters = self._waiters.get(name)

        if waiters is None:
            waiters = weakref.WeakSet()
            self._waiters[name] = waiters

        waiter = EventWaiter(self, name, timeout, filter)
        waiters.add(waiter)
        return waiter

    wait = register_waiter

    def remove_waiter(self, waiter: EventWaiter):
        waiters = self._waiters.get(waiter.name)

        if waiters is None:
            return

        waiters.remove(waiter)

    def push_event(self, name: str, *args, **kwargs):
        name = name.lower()
        handler = self._handlers.get(name)

        if handler is not None:
            evnt = handler(self, *args, **kwargs)
            self.call_listeners(name, evnt)

        else:
            self.call_listeners(name, *args, **kwargs)


    def call_listeners(self, name: str, *args, **kwargs):
        name = name.lower()
        listeners = self._listeners.get(name)
        waiters = self._waiters.get(name)

        if listeners is not None:
            for listener in listeners:
                run_coroutine(listener(*args, **kwargs), self.loop)

        if waiters is not None:
            for waiter in waiters:
                waiter._queue.put_nowait(args)
        
        for subscriber in self._subscribers:
            subscriber.call_listeners(name, *args, **kwargs)

    def on(self, name: Optional[str] = None):
        def wrapped(func):
            nonlocal name
            name = name or func.__name__
            self.register_listener(name, func)

        return wrapped

    def once(self, name: Optional[str] = None):
        def wrapped(func):
            nonlocal name
            name = name or func.__name__

            def callback(*args):
                run_coroutine(func(*args), self.loop)
                self.remove_listener(name, callback)

            self.register_listener(name, callback)

            return func

        return wrapped

    def subscribe(self, pusher: 'EventPusher'):
        pusher._subscribers.append(self)

    def unsubscribe(self, pusher: 'EventPusher'):
        pusher._subscribers.remove(self)

        for name in pusher._listeners:
            self._listeners.pop(name, None)

        for name in pusher._waiters:
            self._waiters.pop(name, None)
