import asyncio
import typing as t

from wsaio import WebSocketClient  # type: ignore

from ..utils import JsonField, JsonObject, JsonTemplate


WebSocketResponseTemplate = JsonTemplate(
    opcode=JsonField('op'),
    sequence=JsonField('s'),
    name=JsonField('t'),
    data=JsonField('d'),
)


class WebSocketResponse(JsonObject, template=WebSocketResponseTemplate):
    opcode: int
    sequence: int
    name: t.Optional[str]
    data: t.Optional[t.Dict[str, t.Any]]


class BaseWebSocket(WebSocketClient):
    if t.TYPE_CHECKING:
        heartbeat_interval: t.Optional[float]
        heartbeat_last_sent: float
        heartbeat_last_acked: float

    def __init__(
        self, loop: t.Optional[asyncio.AbstractEventLoop] = None
    ) -> None:
        super().__init__(loop=loop)  # type: ignore

        self.heartbeat_interval = None

        self.heartbeat_last_sent = float('inf')
        self.heartbeat_last_acked = float('inf')

        self.ready = asyncio.Event()

    @property
    def latency(self) -> float:
        return self.heartbeat_last_acked - self.heartbeat_last_sent

    async def send_heartbeat(self) -> None:
        raise NotImplementedError
