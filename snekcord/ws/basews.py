import asyncio

from wsaio import WebSocketClient

from ..utils import JsonField, JsonTemplate, Notifier


class WebSocketWorker:
    def __init__(self, manager, timeout):
        self.manager = manager
        self.loop = manager.loop

        self.timeout = timeout
        self.timeout_handles = {}

        self.notifier = Notifier(loop=self.loop)

    async def create_connection(self, cls, *args, **kwargs):
        for _ in range(5):
            ws = cls(worker=self)
            try:
                await asyncio.wait_for(
                    ws.connect(*args, **kwargs), self.timeout)
                await asyncio.wait_for(ws._hello_received.wait(), self.timeout)
            except asyncio.TimeoutError:
                continue
            else:
                break
        else:
            raise ConnectionError(f'{cls.__name__} timed out while '
                                  'connecting after 5 attempts')

        self.notifier.register(ws, ws.heartbeat_interval / 1000)

        return ws

    def ack(self, ws):
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

        self._hello_received = asyncio.Event()

    @property
    def ping(self):
        return self.heartbeat_last_acked - self.heartbeat_last_sent

    async def send_heartbeat(self):
        raise NotImplementedError
