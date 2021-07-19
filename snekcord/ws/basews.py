from wsaio import WebSocketClient

from ..utils import JsonField, JsonObject

__all__ = ('BaseWebSocket',)


class WebSocketResponse(JsonObject):
    opcode = JsonField('op')
    sequence = JsonField('s')
    name = JsonField('t')
    data = JsonField('d')


class BaseWebSocket(WebSocketClient):
    def __init__(self, *, loop=None):
        super().__init__(loop=loop)

        self.heartbeat_interval = None

        self.heartbeat_last_sent = float('inf')
        self.heartbeat_last_acked = float('inf')

    @property
    def latency(self):
        return self.heartbeat_last_acked - self.heartbeat_last_sent

    async def send_heartbeat(self):
        raise NotImplementedError
