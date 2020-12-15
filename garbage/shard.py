import aiohttp
import asyncio
import typing as t
import json
import sys
import time

class DiscordResponse:
    def __init__(self, resp: t.Union[bytes, str]):
        self.resp = resp
        try:
            self.loaded = json.loads(self.resp)
            self.opcode = self.loaded.get('op')
            self.sequence = self.loaded.get('s')
            self.event_name = self.loaded.get('t')
            self.data = self.loaded.get('d')
            self.valid = True
        except (AttributeError, ValueError):
            self.opcode = None
            self.sequence = None
            self.event_name = None
            self.event_data = None
            self.valid = False

class ConnectionProtocol(aiohttp.ClientWebSocketResponse):
    def __init__(self, *args, **kwargs):
        self.endpoint: str = None
        self.dispatch: t.Dict[str, t.Any] = None
        self.manager: 'manager.Manager' = None
        self.poll_task: asyncio.Task = None
        self.send_heartbeat: t.Callable[[], None] = None
        self.restart: t.Callable[[bool], None] = None
        self.heartbeat_interval: float = None
        self.waiters: t.Dict[str, t.List[asyncio.Future]] = {}
        super().__init__(*args, **kwargs)

    def create(
        self, 
        *,
        loop: asyncio.AbstractEventLoop, 
        manager: 'manager.Manager', 
        endpoint: str, 
        heartbeat_fn: t.Callable[[], None], 
        dispatch_fn: t.Callable[[DiscordResponse], None],
        restart_fn: t.Callable[[bool], None] = None
    ) -> None:
        self.endpoint = endpoint
        self.manager = manager
        self.send_heartbeat = heartbeat_fn
        self.dispatch = dispatch_fn
        self.restart = restart_fn
        self.loop = loop
        self.poll_task = self.loop.create_task(self.poll_events())

    def wait_for(self, event_name: str) -> asyncio.Future:
        fut = self.manager.loop.create_future()
        waiters = self.waiters.get(event_name)
        if waiters is None:
            waiters.append(fut)
        else:
            self.waiters[event_name] = [fut]
        return fut

    async def poll_events(self) -> None:
        while True:
            resp = await self.receive()
            print(resp)
            if resp.type == aiohttp.WSMsgType.TEXT:
                resp = DiscordResponse(resp.data)
                if resp.valid:
                    for fut in self.waiters.get(resp.event_name, []):
                        fut.set_result(resp)
                    self.waiters[resp.event_name] = []
                    await self.dispatch(resp)
            elif resp.type in (aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED):
                return
            #    await self.restart(resp.data in (1000, 1001))

    async def heartbeat(self) -> None:
        assert self.heartbeat_interval is not None
        while True:
            await self.send_heartbeat()
            await asyncio.sleep(self.heartbeat_interval)

class ConnectionBase:
    def __init__(
        self, 
        manager: 'manager.Manager', 
        loop: asyncio.AbstractEventLoop
    ):
        self.manager = manager
        self.loop = loop

    @property
    def latency(self):
        return self.last_sent - self.last_acked

    @property
    def endpoint(self) -> str:
        raise NotImplementedError

    def send_heartbeat(self) -> None:
        raise NotImplementedError 

    async def dispatch(self, resp: DiscordResponse) -> None:
        raise NotImplementedError

    async def restart(self, can_reconnect: bool) -> None:
        raise NotImplementedError

    async def connect(self) -> None:
        self.heartbeats_sent = 0
        self.heartbeats_acked = 0
        self.last_sent = float('inf')
        self.last_acked = float('inf')
        session = aiohttp.ClientSession(
            ws_response_class=ConnectionProtocol, 
            loop=self.loop
        )
        self.websocket = await session.ws_connect(self.endpoint)
        self.websocket.create(
            loop=self.loop,
            manager=self.manager,
            endpoint=self.endpoint, 
            heartbeat_fn=self.send_heartbeat, 
            dispatch_fn=self.dispatch,
            restart_fn=self.restart
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

class Shard(ConnectionBase):
    @property
    def endpoint(self) -> str:
        return 'wss://gateway.discord.gg?v=6'

    @property
    def heartbeat_payload(self) -> t.Dict[str, t.Any]:
        payload = {
            'op': ShardOpcode.HEARTBEAT,
            'd': None
        }
        return payload

    @property
    def identify_payload(self) -> t.Dict[str, t.Any]:
        payload = {
            'op': ShardOpcode.IDENTIFY,
            'd': {
                'token': self.manager.token,
                #'intents': self.manager.intents,
                'properties': {
                    '$os': sys.platform,
                    '$browser': 'wrapper-we-dont-name-for',
                    '$device': '^'
                }
            }
        }
        return payload
    
    async def send_heartbeat(self):
        await self.websocket.send_json(self.heartbeat_payload)
        self.heartbeats_sent += 1
        self.last_sent = time.monotonic()

    async def restart(self, can_reconnect: bool) -> None:
        self.websocket.poll_task.cancel()
        self.websocket.heartbeat_task.cancel()
        # ...

    async def dispatch(self, resp: DiscordResponse) -> None:
        if resp.opcode == ShardOpcode.HELLO:
            await self.websocket.send_json(self.identify_payload)
            self.websocket.heartbeat_interval = resp.data['heartbeat_interval'] / 1000
            self.websocket.heartbeat_task = self.loop.create_task(self.websocket.heartbeat())
        elif resp.opcode == ShardOpcode.HEARTBEAT_ACK:
            self.heartbeats_acked += 1
            self.last_acked = time.monotonic()
        elif resp.opcode == ShardOpcode.DISPATCH:
            self.manager.dispatch(resp)