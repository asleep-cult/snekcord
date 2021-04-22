from __future__ import annotations

import asyncio
import json

from wsaio import WebSocketClient

from ..utils.cycler import Cycler
from ..utils.events import EventDispatcher
from ..utils.json import JsonField, JsonTemplate


class Heartbeater(Cycler):
    def __init__(self, connection: BaseConnection, *args, **kwargs) -> None:
        self.timeout = kwargs.pop('timeout', 0)
        super().__init__(*args, **kwargs)
        self.connection = connection

    async def run(self) -> None:
        try:
            await asyncio.wait_for(self.connection.send_heartbeat(),
                                   timeout=self.timeout)
        except asyncio.TimeoutError:
            pass


WebSocketResponse = JsonTemplate(
    opcode=JsonField('op'),
    sequence=JsonField('s'),
    name=JsonField('t'),
    data=JsonField('d'),
).default_object()


class BaseConnection(WebSocketClient):
    def __init__(self, manager: EventDispatcher) -> None:
        super().__init__(loop=manager.loop)
        self.manager = manager
        self.heartbeater = None

    @property
    def heartbeat_payload(self) -> dict:
        raise NotImplementedError

    async def send_json(self, data: dict, *args, **kwargs) -> None:
        await self.send_str(json.dumps(data), *args, **kwargs)

    async def send_heartbeat(self):
        await self.send_json(self.heartbeat_payload, drain=True)
