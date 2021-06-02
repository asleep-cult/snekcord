import asyncio
from typing import Any, Dict, NoReturn, Optional, Type, TypeVar

from wsaio import WebSocketClient

from ..manager import Manager
from ..utils import JsonObject

_T = TypeVar('_T')

class WebSocketWorker:
    loop: asyncio.AbstractEventLoop
    manager: Manager
    def __init__(self, *, manager: Manager, timeout: float) -> None: ...
    async def create_connection(self, cls: Type[_T], *args: Any, **kwargs: Any) -> _T: ...
    def ack(self, ws: Any) -> None: ...
    async def work(self) -> None: ...

class WebSocketResponse(JsonObject):
    opcode: int
    sequence: int
    name: Optional[str]
    data: Optional[Dict[str, Any]]

class BaseWebSocket(WebSocketClient):
    heartbeat_interval: Optional[float]
    heartbeat_last_acked: float
    heartbeat_last_sent: float
    ready: asyncio.Event

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None: ...

    @property
    def latency(self) -> float: ...
    async def send_heartbeat(self) -> NoReturn: ...
