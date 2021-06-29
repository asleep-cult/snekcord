import asyncio

from wsaio import WebSocketClient

__all__ = ('BaseWebSocket',)


class BaseWebSocket(WebSocketClient):
    heartbeat_interval: float | None
    heartbeat_last_sent: float
    heartbeat_last_acked: float

    def __init__(self, *, loop:  asyncio.AbstractEventLoop | None = ...
                 ) -> None: ...

    @property
    def latency(self) -> float: ...

    async def send_heartbeat(self) -> None: ...
