import asyncio
import weakref

from .exceptions import InvalidPusherHandler


class EventWaiter:
    def __init__(self, pusher, name, timeout, filter):
        self.pusher = pusher
        self.name = name
        self.timeout = timeout
        self.filter = filter
        self._new_future()

    def _new_future(self):
        self.future = self.handler.loop.create_future()

    def _do_wait(self):
        return asyncio.wait_for(self.future, timeout=self.timeout)

    def __aiter__(self):
        return self

    async def __anext__(self):
        ret = await self._do_wait()
        self._new_future()
        return ret

    async def __await__impl(self):
        try:
            ret = await self._do_wait()
        finally:
            self._cleanup()
        return ret

    def __await__(self):
        return self.__await__impl().__await__()

    def _cleanup(self):
        self.pusher.remove_waiter(self)

    __del__ = _cleanup


def run_coroutine(coro, loop):
    if asyncio.iscoroutine(coro):
        loop.create_task(coro)


class EventPusher:
    def __init__(self, loop):
        self.loop = loop
        self._handlers = {handler.name: handler for handler in self.handlers}
        self._listeners = {handler.name: [] for handler in self.handlers}
        self._waiters = {handler.name: weakref.WeakSet() for handler in self.handlers}

        for name, listeners in self._listeners.items():
            try:
                listeners.append(getattr(self, name))
            except AttributeError:
                continue

    def register_listener(self, name, func):
        name = name.lower()
        listeners = self._listeners.get(name)

        if listeners is None:
            raise InvalidPusherHandler(self, name)

        listeners.append(func)

    def remove_listener(self, name, func):
        name = name.lower()
        listeners = self._listeners.get(name)

        if listeners is None:
            raise InvalidPusherHandler(self, name)

        listeners.remove(func)

    def register_waiter(self, name, *, timeout=0, filter=None):
        name = name.lower()
        waiters = self._waiters.get(name)

        if waiters is None:
            raise InvalidPusherHandler(self, name)

        waiter = EventWaiter(self, name, timeout, filter)
        waiters.add(waiter)

        return waiter

    wait = register_waiter

    def remove_waiter(self, waiter):
        waiters = self._waiters.get(waiter.name)

        if waiters is None:
            raise InvalidPusherHandler(self, waiter.name)

        try:
            waiter.future.cancel()
        except asyncio.InvalidStateError:
            pass

        waiters.remove(waiter)

    def push_event(self, name, *args, **kwargs):
        name = name.lower()
        handler = self._handlers.get(name)

        if handler is None:
            raise InvalidPusherHandler(self, name)

        event = handler._execute(self, *args, **kwargs)
        self.call_listeners(name, event)

    def call_listeners(self, name, *args):
        name = name.lower()
        listeners = self._listeners.get(name)
        waiters = self._waiters.get(name)

        if listeners is None or waiters is None:
            raise InvalidPusherHandler(self, name)

        for listener in listeners:
            run_coroutine(listener(*args), self.loop)

        for waiter in waiters:
            if waiter.filter is not None:
                if not waiter.filter(*args):
                    continue

            if len(args) > 1:
                waiter.future.set_result(args)
            else:
                waiter.future.set_result(*args)
