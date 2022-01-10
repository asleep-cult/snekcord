import functools
import signal
import socket

from loguru import logger

from .client import Client
from .listeners import (
    ChannelEvent,
    ChannelListener,
    GuildEvent,
    GuildListener,
    WebSocketIntents,
    WebSocketListener,
)
from ..exceptions import UnknownListenerError
from ..rest.endpoints import (
    GET_GATEWAY,
    GET_GATEWAY_BOT,
)
from ..websockets.shard_websocket import ShardWebSocket

__all__ = (
    'WebSocketIntents',
    'WebSocketListener',
    'WebSocketClient',
)


class WebSocketClient(Client):
    def __init__(self, authorization, *, loop=None, shard_ids=None):
        super().__init__(authorization, loop=loop)

        if not self.authorization.ws_connectable():
            raise TypeError(f'Cannot connect to gateway using {authorization.type.name} token')

        if shard_ids is not None:
            self.shard_ids = [int(shard_id) for shard_id in shard_ids]
        else:
            self.shard_ids = None

        self._shards = {}
        self._listeners = {}
        self._events = {}

    def get_intents(self):
        func = lambda intents, listener: intents | listener.get_intents()
        return functools.reduce(func, self._listeners.values(), 0)

    def get_shard(self, shard_id: int):
        if shard_id not in self.shard_ids:
            raise ValueError(f'Invalid shard id: {shard_id!r}')

        return self._shards[shard_id]

    def create_channel_listener(self, *, direct_messages=False):
        listener = ChannelListener(client=self)
        self._listeners[WebSocketListener.CHANNEL_EVENTS] = listener

        if direct_messages:
            listener.enable_direct_messages()

        for event in ChannelEvent:
            self._events[event] = listener

        return listener

    def create_guild_listener(self):
        listener = GuildListener(client=self)
        self._listeners[WebSocketListener.GUILD_EVENTS] = listener

        for event in GuildEvent:
            self._events[event] = listener

        return listener

    def get_listener(self, type):
        try:
            return self._listeners[type]
        except KeyError:
            raise UnknownListenerError(type) from None

    def get_channel_listener(self):
        return self.get_listener(WebSocketListener.CHANNEL_EVENTS)

    def get_guild_listener(self):
        return self.get_listener(WebSocketListener.GUILD_EVENTS)

    def get_listener_for(self, event: str):
        return self._events.get(event)

    async def fetch_gateway(self):
        if self.authorization.is_bot():
            endpoint = GET_GATEWAY_BOT
        else:
            endpoint = GET_GATEWAY

        return await self.rest.request(endpoint)

    async def connect(self) -> None:
        gateway = await self.fetch_gateway()

        if self.shard_ids is None:
            shards = gateway.get('shards', 1)
            self.shard_ids = list(range(shards))

        for shard_id in self.shard_ids:
            shard = ShardWebSocket(self, gateway['url'])
            self._shards[shard_id] = shard

            await shard.connect()
            logger.debug(f'Shard {shard_id + 1}/{self.shard_ids[-1] + 1} connected')

        future = self.loop.create_future()

        def set_future_result():
            future.set_result(None)

        async def wait_for_interrupt():
            await future
            logger.debug('Client received signal to shutdown')

        try:
            self.loop.add_signal_handler(signal.SIGINT, set_future_result)
            self.loop.add_signal_handler(signal.SIGTERM, set_future_result)
        except NotImplementedError:
            signal.signal(signal.SIGINT, lambda signum, frame: None)
            signal.signal(signal.SIGTERM, lambda signum, frame: None)

            ssock, csock = socket.socketpair()
            signal.set_wakeup_fd(ssock.fileno())

            def signal_handler(task):
                signums = set(task.result())
                if signums.intersection((signal.SIGINT, signal.SIGTERM)):
                    set_future_result()
                else:
                    signal_reader()

            def signal_reader():
                task = self.loop.create_task(self.loop.sock_recv(csock, 4096))
                task.add_done_callback(signal_handler)

            signal_reader()

        await wait_for_interrupt()

        try:
            self.loop.remove_signal_handler(signal.SIGINT)
            self.loop.remove_signal_handler(signal.SIGTERM)
        except NotImplementedError:
            signal.set_wakeup_fd(-1)

            signal.signal(signal.SIGINT, signal.default_int_handler)
            signal.signal(signal.SIGTERM, signal.SIG_DFL)

        for shard_id, shard in self._shards.items():
            if shard.ws is not None:
                try:
                    await shard.ws.close()
                except Exception:
                    logger.warning(f'Error while closing shard {shard_id}')
                else:
                    logger.debug(f'Shard {shard_id + 1}/{self.shard_ids[-1] + 1} closed')

        await self.rest.aclose()