import asyncio
import weakref


class EventWaiter:
    def __init__(self, pusher, name, timeout, filter):
        self.pusher = pusher
        self.name = name
        self.timeout = timeout
        self.filter = filter
        self._queue = asyncio.Queue()

    async def _do_wait(self):
        coro = self._queue.get()
        ret = await asyncio.wait_for(coro, timeout=self.timeout)
        if len(ret) == 1:
            return ret[0]
        return ret

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


def run_coroutine(coro, loop):
    if asyncio.iscoroutine(coro):
        loop.create_task(coro)


class EventPusher:
    handlers = ()

    def __init__(self, loop):
        self.loop = loop
        self._handlers = {handler.name: handler for handler in self.handlers}
        self._listeners = {}
        self._waiters = {}
        self._subscribers = []

    def register_listener(self, name, func):
        name = name.lower()
        listeners = self._listeners.get(name)

        if listeners is None:
            listeners = []
            self._listeners[name] = listeners

        listeners.append(func)

    def remove_listener(self, name, func):
        name = name.lower()
        listeners = self._listeners.get(name)

        if listeners is None:
            return

        listeners.remove(func)

    def register_waiter(self, name, *, timeout=None, filter=None):
        name = name.lower()
        waiters = self._waiters.get(name)

        if waiters is None:
            waiters = weakref.WeakSet()
            self._waiters[name] = waiters

        waiter = EventWaiter(self, name, timeout, filter)
        waiters.add(waiter)
        return waiter

    wait = register_waiter

    def remove_waiter(self, waiter):
        waiters = self._waiters.get(waiter.name)

        if waiters is None:
            return

        waiters.remove(waiter)

    def push_event(self, name, *args, **kwargs):
        name = name.lower()
        handler = self._handlers.get(name)

        if handler is not None:
            listener_args = (handler._execute(self, *args, **kwargs),)
        else:
            listener_args = args

        self.call_listeners(name, *listener_args)

        for subscriber in self._subscribers:
            subscriber.call_listeners(name, *listener_args)

    def call_listeners(self, name, *args):
        name = name.lower()
        listeners = self._listeners.get(name)
        waiters = self._waiters.get(name)

        if listeners is not None:
            for listener in listeners:
                run_coroutine(listener(*args), self.loop)

        if waiters is not None:
            for waiter in waiters:
                if waiter.filter is not None:
                    if not waiter.filter(*args):
                        continue

                waiter._queue.put_nowait(args)

    def on(self, func):
        self.register_listener(func.__name__, func)
        return func

    def once(self, func):
        def callback(*args):
            run_coroutine(func(*args), self.loop)
            self.remove_listener(func.__name__, callback)

        self.register_listener(func.__name__, callback)
        return func

    def subscribe(self, pusher):
        pusher._subscribers.append(self)

    def unsubscribe(self, pusher):
        pusher._subscribers.remove(self)

        for name in pusher._listeners:
            self._listeners.pop(name, None)

        for name in pusher._waiters:
            self._waiters.pop(name, None)
