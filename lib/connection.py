import aiohttp
import asyncio
import json
import sys
import time
import functools

from .utils import (
    JsonStructure,
    JsonField
)

from typing import (
    Dict,
    Union,
    Any, 
    Callable,
    Awaitable
)

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

class DiscordResponse(JsonStructure):
    opcode = JsonField('op', int)
    sequence = JsonField('s', int)
    event_name = JsonField('t')
    data = JsonField('d')

class ConnectionProtocol(aiohttp.ClientWebSocketResponse):
    def new(
        self, 
        *,
        loop: asyncio.AbstractEventLoop,
        heartbeat_payload: Dict[str, Any],
        dispatch_function: Callable[[DiscordResponse], None]
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

        self.do_poll()

    def do_heartbeat(self) -> None:
        interval = self.heartbeat_interval if self.heartbeats_sent != 0 else 0
        create_task = functools.partial(self.loop.create_task, self.send_heartbeat())
        self.current_heartbeat_handle = self.loop.call_later(interval, create_task)

    async def send_heartbeat(self) -> None:
        assert self.heartbeat_interval != float('inf'), 'hello not received'

        await self.send_json(self.heartbeat_payload)
        self.heartbeats_sent += 1
        self.last_sent = time.monotonic()
        self.do_heartbeat()

    def heartbeat_ack(self) -> None:
        self.heartbeats_acked += 1
        self.last_acked = time.monotonic()

    def do_poll(self) -> None:
        create_task = functools.partial(self.loop.create_task, self.poll_event())
        self.current_poll_handle = self.loop.call_soon(create_task)

    async def poll_event(self) -> None:
        payload = await self.receive()
        if payload.type == aiohttp.WSMsgType.TEXT:
            resp = DiscordResponse.unmarshal(payload.data)
            await self.dispatch_function(resp)

        elif payload.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING):
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
        return  self.last_acked - self.last_sent  

class ConnectionBase:
    def __init__(self, client, endpoint):
        self._client = client
        self.endpoint = endpoint

    @property
    def heartbeat_payload(self) -> Dict[str, Any]:
        raise NotImplementedError

    def dispatch(self, resp: DiscordResponse) -> None:
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
            dispatch_function=self.dispatch
        )

class Shard(ConnectionBase):
    def __init__(self, client, endpoint, shard_id):
        super().__init__(client, endpoint)
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
                'token': self._client.token,
                #'intents': self.manager.intents,
                'properties': {
                    '$os': sys.platform,
                    '$browser': 'wrapper-we-dont-name-for',
                    '$device': '^'
                }
            }
        }
        if self._client.ws.sharded:
            payload['shard'] = [self.id, self._client.ws.recommended_shards]
        return payload

    async def dispatch(self, resp: DiscordResponse) -> None:
        if resp.opcode == ShardOpcode.HELLO:
            await self.websocket.send_json(self.identify_payload)
            
            self.websocket.heartbeat_interval = resp.data['heartbeat_interval'] / 1000
            self.websocket.do_heartbeat()

        elif resp.opcode == ShardOpcode.HEARTBEAT_ACK:
            self.websocket.heartbeat_ack()

        elif resp.opcode == ShardOpcode.DISPATCH:
            self._client.events.dispatch(resp)