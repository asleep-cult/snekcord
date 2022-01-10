import asyncio
import enum
import inspect
from collections import defaultdict
from typing import Callable, Optional, TypeVar

__all__ = (
    'WebSocketListener',
    'WebSocketIntents',
)

T = TypeVar('T')

WaiterFilter = Optional[Callable[[T], bool]]


class WebSocketIntents(enum.IntFlag):
    GUILDS = 1 << 0
    GUILD_MEMBERS = 1 << 1
    GUILD_BANS = 1 << 2
    GUILD_EMOJIS_AND_STICKERS = 1 << 3
    GUILD_INTEGRATIONS = 1 << 4
    GUILD_WEBHOOKS = 1 << 5
    GUILD_INVITES = 1 << 6
    GUILD_VOICE_STATES = 1 << 7
    GUILD_PRESENCES = 1 << 8
    GUILD_MESSAGES = 1 << 9
    GUILD_MESSAGE_REACTIONS = 1 << 10
    GUILD_MESSAGE_TYPING = 1 << 11
    DIRECT_MESSAGES = 1 << 12
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    DIRECT_MESSAGE_TYPING = 1 << 14
    GUILD_SCHEDULED_EVENTS = 1 << 16


class WebSocketListener(enum.IntEnum):
    CHANNEL_EVENTS = enum.auto()
    GUILD_EVENTS = enum.auto()
    BAN_EVENTS = enum.auto()
    MEMBER_EVENTS = enum.auto()
    INTEGRATION_EVENTS = enum.auto()
    INVITE_EVENTS = enum.auto()
    MESSAGE_EVENTS = enum.auto()
    MESSAGE_REACTION_EVENTS = enum.auto()
    MESSAGE_TYPING_EVENTS = enum.auto()
    STAGE_EVENTS = enum.auto()
    VOICE_EVENTS = enum.auto()
    EMOJI_EVENTS = enum.auto()
    STICKER_EVENTS = enum.auto()
    PRESENCE_EVENTS = enum.auto()
    USER_EVENTS = enum.auto()
    WEBHOOK_EVENTS = enum.auto()


class _WebSocketEventWaiter:
    def __init__(self, listener, event, *, timeout=None, filter=None):
        self.listener = listener
        self.event = event
        self.timeout = timeout
        self.filter = filter

        self.queue = asyncio.Queue()
        self.future = None
        self.closed = False

    def put(self, *args):
        if self.filter is None or self.filter(*args):
            self.queue.put_nowait(args)

    async def get(self):
        if self.closed:
            raise RuntimeError('get() called on closed waiter')

        if self.future is not None:
            raise RuntimeError('Cannot wait for multiple events')

        self.future = asyncio.wait_for(self.queue.get(), timeout=self.timeout)
        result = await self.future

        if len(result) == 0:
            return result[0]

        return result

    def cleanup(self):
        if self.closed:
            raise RuntimeError('cleanup() called on closed waiter')

        waiters = self.listener.waiters[self.event]
        waiters.remove(self)

        if self.future is not None:
            try:
                self.future.cancel()
            except asyncio.InvalidStateError:
                pass

        self.closed = True

    def __await__(self):
        try:
            result = yield from self.get().__await__()
            return result
        finally:
            self.cleanup()

    async def __aiter__(self):
        while True:
            try:
                yield await self.get()
            except GeneratorExit:
                self.cleanup()
                raise
            else:
                self.future = None


class BaseWebSocketListener:
    __slots__ = ('_callbacks', '_waiters', '_dispatchers')

    def __init__(self, *, client):
        self.client = client
        self._callbacks = defaultdict(list)
        self._waiters = defaultdict(list)

        self._dispatchers = {}
        for name, func in inspect.getmembers(self, inspect.isfunction):
            if name.startswith('dispatch_'):
                self._dispatchers[self.get_event(name[9:])] = func

    def __repr__(self):
        return f'{self.__class__.__name__}(client={self.client!r})'

    def get_event(self, name):
        raise NotImplementedError

    def get_intents(self):
        raise NotImplementedError

    def add_handler(self, handler):
        handler.register_callbacks(self)

    def create_waiter(self, event, *, timeout=None, filter=None):
        event = self.get_event(event)

        waiter = _WebSocketEventWaiter(self, event, timeout=timeout, filter=filter)
        self._waiters[event].append(waiter)

        return waiter

    def register_callback(self, event, callback):
        event = self.get_event(event)
        self._waiters[event].append(callback)

    def unregister_callback(self, event, callback):
        event = self.get_event(event)

        try:
            self._callbacks[event].remove(callback)
        except ValueError:
            raise RuntimeError(f'Callback {callback!r} is not registered for {event!r}') from None

    async def dispatch(self, event, payload):
        event = self.get_event(event)
        evt = await self._dispatchers[event](payload)

        callbacks = self._callbacks[event]
        for callback in callbacks:
            self.client.loop.create_task(callback(evt))

        waiters = self._waiters[event]
        for waiter in waiters:
            waiter.put(evt)