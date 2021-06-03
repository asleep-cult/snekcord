import asyncio
import time

from wsaio import WebSocketClient

from ..utils import JsonField, JsonTemplate, Notifier


class BaseWebSocketWorker:
    def __init__(self, *, manager, timeout):
        self.manager = manager
        self.loop = manager.loop

        self.timeout = timeout
        self.timeout_handles = {}

        self.notifier = Notifier(loop=self.loop)

    async def create_connection(self, *args, **kwargs):
        raise NotImplementedError

    def ack(self, ws):
        ws.heartbeat_last_acked = time.perf_counter()
        handle = self.timeout_handles.pop(ws, None)
        if handle is not None:
            handle.cancel()

    async def work(self):
        while True:
            ws = await self.notifier.wait()

            handle = self.timeout_handles.pop(ws, None)
            if handle is not None:
                handle.cancel()
            else:
                self.timeout_handles[ws] = self.loop.call_later(
                    self.timeout, lambda: None)
                await ws.send_heartbeat()


WebSocketResponse = JsonTemplate(
    opcode=JsonField('op'),
    sequence=JsonField('s'),
    name=JsonField('t'),
    data=JsonField('d'),
).default_object('WebSocketResponse')


class BaseWebSocket(WebSocketClient):
    def __init__(self, loop):
        super().__init__(loop=loop)

        self.heartbeat_interval = None

        self.heartbeat_last_sent = float('inf')
        self.heartbeat_last_acked = float('inf')

        self.ready = asyncio.Event()

    @property
    def latency(self):
        return self.heartbeat_last_acked - self.heartbeat_last_sent

    async def send_heartbeat(self):
        raise NotImplementedError
