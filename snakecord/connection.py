import asyncio
import functools
import sys
import threading
import time
from typing import Any, Awaitable, Callable, Dict, Optional, TYPE_CHECKING

import aiohttp

from .exceptions import InvalidPusherHandler
from .enums import ShardOpcode, VoiceConnectionOpcode, SpeakingState
from .utils import JsonField, JsonStructure


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

    @property
    def latency(self) -> float:
        return self.last_acked - self.last_sent


class ConnectionBase:
    def __init__(self, event_pusher, endpoint):
        self.event_pusher = event_pusher
        self.endpoint = endpoint
        self.websocket = None

    @property
    def heartbeat_payload(self) -> Dict[str, Any]:
        raise NotImplementedError

    def dispatch(self, resp: DiscordResponse) -> None:
        raise NotImplementedError

    def handle_zombie_connection(self):
        raise NotImplementedError

    async def connect(self) -> None:
        session = aiohttp.ClientSession(
            loop=self.event_pusher.loop,
            ws_response_class=ConnectionProtocol
        )

        self.websocket: ConnectionProtocol = await session.ws_connect(self.endpoint)

        self.websocket.new(
            loop=self.event_pusher.loop,
            heartbeat_payload=self.heartbeat_payload,
            dispatch_function=self.dispatch,
            zombie_function=self.handle_zombie_connection
        )


class Shard(ConnectionBase):
    def __init__(self, sharder, endpoint, shard_id):
        super().__init__(sharder, endpoint)
        self.id = shard_id

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
                'token': self.event_pusher.token,
                # 'intents': self.manager.intents,
                'properties': {
                    '$os': sys.platform,
                    '$browser': 'wrapper-we-dont-name-for',
                    '$device': '^'
                }
            }
        }
        if self.event_pusher.multi_sharded:
            payload['shard'] = [self.id, self.event_pusher.recommended_shards]
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
            try:
                self.event_pusher.push_event(resp.event_name, resp.data)
            except InvalidPusherHandler:
                pass  # Unknown event


class VoiceWSProtocol(ConnectionBase):
    def __init__(self, voice_connection):
        self.voice_connection = voice_connection
        super().__init__(voice_connection.client, voice_connection.endpoint)

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

    async def send_speaking(self, state=SpeakingState.VOICE):
        payload = {
            'op': VoiceConnectionOpcode.SPEAKING,
            'd': {
                'speaking': state.value,
                'delay': 0
            }
        }
        await self.websocket.send_json(payload)

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
        else:
            await self.voice_connection.datagram_received(data)

    def datagram_received(self, data, addr):
        self.voice_connection.loop.create_task(self._datagram_received(data))
