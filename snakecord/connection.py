import aiohttp
import asyncio
import sys
import time
import functools
import threading

from . import logger
from .utils import JsonStructure, JsonField
from typing import Dict, Any, Callable, Awaitable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client


class ShardOpcode:
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11


class VoiceConnectionOpcode:
    IDENTIFY = 0
    SELECT = 1
    READY = 2
    HEARTBEAT = 3
    SESSION_DESCRIPTION = 4
    SPEAKING = 5
    HEARTBEAT_ACK = 6
    RESUME = 7
    HELLO = 8
    RESUMED = 9
    CLIENT_DISCONNECT = 13


class DiscordResponse(JsonStructure):
    __json_fields__ = {
        'opcode': JsonField('op', int),
        'sequence': JsonField('s', int),
        'event_name': JsonField('t'),
        'data': JsonField('d')
    }

    opcode: Optional[int]
    sequence: Optional[int]
    event_name: Optional[str]
    data: Optional[dict]


class ConnectionProtocol(aiohttp.ClientWebSocketResponse):
    def new(
        self,
        *,
        loop: asyncio.AbstractEventLoop,
        heartbeat_payload: Dict[str, Any],
        dispatch_function: Callable[[DiscordResponse], None],
        zombie_function
    ) -> None:

        self.loop = loop

        self.heartbeat_payload = heartbeat_payload
        self.dispatch_function = dispatch_function

        self.heartbeat_interval = float('inf')
        self.last_sent = float('inf')
        self.last_acked = float('inf')

        self.heartbeats_sent = 0
        self.heartbeats_acked = 0

        self.current_heartbeat_handle: asyncio.Handle = None
        self.current_poll_handle: asyncio.Handle = None
        self.current_zombie_thread = None

        self.zombie_function = zombie_function

        self.waiters = {}

        self.do_poll()

    def _zombie_connection(self):
        if self.current_zombie_thread.cancelled:
            return
        self.zombie_function()
        self.current_zombie_thread = None

    def do_heartbeat(self) -> None:
        interval = self.heartbeat_interval if self.heartbeats_sent != 0 else 0
        create_task = functools.partial(
            self.loop.create_task,
            self.send_heartbeat()
        )
        self.current_heartbeat_handle = \
            self.loop.call_later(interval, create_task)
        self.current_zombie_thread = threading.Timer(
            interval + 10,
            self._zombie_connection
        )
        self.current_zombie_thread.cancelled = False
        self.current_zombie_thread.start()

    async def send_heartbeat(self) -> None:
        assert self.heartbeat_interval != float('inf'), 'HELLO not received'

        await self.send_json(self.heartbeat_payload)
        self.heartbeats_sent += 1
        self.last_sent = time.monotonic()
        self.do_heartbeat()

    def heartbeat_ack(self) -> None:
        self.heartbeats_acked += 1
        self.last_acked = time.monotonic()

        if self.current_zombie_thread is not None:
            self.current_zombie_thread.cancelled = True
            self.current_zombie_thread.cancel()

    def do_poll(self) -> None:
        create_task = functools.partial(
            self.loop.create_task,
            self.poll_event()
        )
        self.current_poll_handle = self.loop.call_soon(create_task)

    async def poll_event(self) -> None:
        payload = await self.receive()
        if payload.type == aiohttp.WSMsgType.TEXT:
            resp = DiscordResponse.unmarshal(payload.data)

            if resp.event_name is not None:
                waiters = self.waiters.pop(resp.event_name.lower(), [])
                for waiter in waiters:
                    waiter.set_result(resp)

            await self.dispatch_function(resp)

        elif payload.type in (
            aiohttp.WSMsgType.CLOSE,
            aiohttp.WSMsgType.CLOSED,
            aiohttp.WSMsgType.CLOSING,
            aiohttp.WSMsgType.ERROR,
        ):
            return

        self.do_poll()

    def close(self, *args, **kwargs) -> Awaitable:
        if self.current_heartbeat_handle is not None:
            self.current_heartbeat_handle.cancel()

        if self.current_poll_handle is not None:
            self.current_poll_handle.cancel()

        return super().close(*args, **kwargs)

    def wait_for(self, event):
        waiters = self.waiters.get(event.lower())
        if waiters is None:
            waiters = []
            self.waiters[event] = waiters
        fut = self.loop.create_future()
        waiters.append(fut)
        return fut

    @property
    def latency(self) -> float:
        return self.last_acked - self.last_sent


class ConnectionBase:
    def __init__(self, client: 'Client', endpoint: str):
        self._client = client
        self.endpoint = endpoint
        self.websocket: ConnectionProtocol = None

    @property
    def heartbeat_payload(self) -> Dict[str, Any]:
        raise NotImplementedError

    def dispatch(self, resp: DiscordResponse) -> None:
        raise NotImplementedError

    def handle_zombie_connection(self):
        raise NotImplementedError

    async def connect(self) -> None:
        session = aiohttp.ClientSession(
            loop=self._client.loop,
            ws_response_class=ConnectionProtocol
        )

        self.websocket: ConnectionProtocol = await session.ws_connect(
            self.endpoint
        )

        self.websocket.new(
            loop=self._client.loop,
            heartbeat_payload=self.heartbeat_payload,
            dispatch_function=self.dispatch,
            zombie_function=self.handle_zombie_connection
        )


class Shard(ConnectionBase):
    def __init__(self, client, endpoint, shard_id):
        super().__init__(client, endpoint)
        self.id = shard_id

    def handle_zombie_connection(self):
        logger.CONNECTION_LOGGER.critical(
            'Shard ID %s hasn\'t received a heartbeat'
            'ack from the gateway in %s',
            self.id, time.monotonic() - self.websocket.last_acked,
            stack_info=True,
            extra=dict(cls=self.__class__.__name__)
        )

    @property
    def heartbeat_payload(self) -> Dict[str, Any]:
        payload = {
            'op': ShardOpcode.HEARTBEAT,
            'd': None
        }
        return payload

    @property
    def identify_payload(self) -> Dict[str, Any]:
        payload = {
            'op': ShardOpcode.IDENTIFY,
            'd': {
                'token': self._client.token,
                # 'intents': self.manager.intents,
                'properties': {
                    '$os': sys.platform,
                    '$browser': 'wrapper-we-dont-name-for',
                    '$device': '^'
                }
            }
        }
        if self._client.ws.multi_sharded:
            payload['shard'] = [self.id, self._client.ws.recommended_shards]
        return payload

    async def update_voice_state(
        self,
        guild_id,
        channel_id,
        self_mute=False,
        self_deaf=False
    ):
        payload = {
            'op': ShardOpcode.VOICE_STATE_UPDATE,
            'd': {
                'guild_id': guild_id,
                'channel_id': channel_id,
                'self_mute': self_mute,
                'self_deaf': self_deaf
            }
        }

        await self.websocket.send_json(payload)

        voice_state_update = self.websocket.wait_for('voice_state_update')
        voice_server_update = self.websocket.wait_for('voice_server_update')

        return voice_state_update, voice_server_update

    async def dispatch(self, resp: DiscordResponse) -> None:
        if resp.opcode == ShardOpcode.HELLO:
            await self.websocket.send_json(self.identify_payload)

            self.websocket.heartbeat_interval = \
                resp.data['heartbeat_interval'] / 1000
            self.websocket.do_heartbeat()

        elif resp.opcode == ShardOpcode.HEARTBEAT_ACK:
            self.websocket.heartbeat_ack()

        elif resp.opcode == ShardOpcode.DISPATCH:
            self._client.events.dispatch(resp)


class VoiceWSProtocol(ConnectionBase):
    def __init__(self, voice_connection):
        self.voice_connection = voice_connection
        super().__init__(voice_connection._client, voice_connection.endpoint)

    @property
    def heartbeat_payload(self):
        payload = {
            'op': VoiceConnectionOpcode.HEARTBEAT,
            'd': 0
        }
        return payload

    @property
    def identify_payload(self):
        payload = {
            'op': VoiceConnectionOpcode.IDENTIFY,
            'd': {
                'server_id': self.voice_connection.guild_id,
                'user_id': self.voice_connection.voice_state.member.user.id,
                'session_id': self.voice_connection.voice_state.session_id,
                'token': self.voice_connection.token
            }
        }
        return payload

    @property
    def select_payload(self):
        payload = {
            'op': VoiceConnectionOpcode.SELECT,
            'd': {
                'protocol': 'udp',
                'data': {
                    'address': self.voice_connection.protocol.ip,
                    'port': self.voice_connection.protocol.port,
                    'mode': self.voice_connection.mode
                }
            }
        }
        return payload

    async def select(self):
        await self.websocket.send_json(self.select_payload)

    async def dispatch(self, resp):
        if resp.opcode == VoiceConnectionOpcode.HELLO:
            await self.websocket.send_json(self.identify_payload)

            self.websocket.heartbeat_interval = \
                resp.data['heartbeat_interval'] / 1000
            self.websocket.do_heartbeat()

        elif resp.opcode == VoiceConnectionOpcode.HEARTBEAT_ACK:
            self.websocket.heartbeat_ack()

        else:
            await self.voice_connection.dispatch(resp)


class VoiceUDPProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.ip = None
        self.port = None
        self.mode = None
        self.selected = False
        self.voice_connection = None

    async def _datagram_received(self, data):
        if not self.selected:
            end = data.index(0, 4)
            ip = data[4:end]
            self.ip = ip.decode()

            port = data[-2:]
            self.port = int.from_bytes(port, 'big')

            await self.voice_connection.ws.select()
            self.selected = True

    def datagram_received(self, data, addr):
        self.voice_connection.loop.create_task(self._datagram_received(data))
