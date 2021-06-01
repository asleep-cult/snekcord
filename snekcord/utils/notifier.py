import asyncio

__all__ = ('Notifier',)


class Notifier:
    def __init__(self, loop=None):
        if loop is not None:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()

        self.handles = {}
        self.queue = asyncio.Queue()

    def register(self, obj, interval=0):
        self._put(obj, interval)

    def unregister(self, obj):
        handle = self.handles[obj]
        handle.cancle()
        return handle

    def _put(self, obj, interval):
        self.queue.put_nowait(obj)
        self.handles[obj] = self.loop.call_later(
            interval, self._put, obj, interval)

    async def wait(self):
        return await self.queue.get()
