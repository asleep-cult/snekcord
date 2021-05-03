import asyncio
from typing import Any, Callable, Optional


class Cycler:
    def __init__(self, *,
                 loop: Optional[asyncio.AbstractEventLoop] = None,
                 delay: float,
                 callback: Optional[Callable[..., Any]] = None) -> None:
        if loop is not None:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()

        self.delay = delay
        self.callback = callback
        self.cancelled = False
        self._task = None
        self._handle: Optional[asyncio.TimerHandle] = None

    def _schedule_callback(self, delay: bool = True) -> None:
        if not self.cancelled:
            if delay:
                self._handle = self.loop.call_later(self.delay,
                                                    self._actual_callback)
            else:
                self.loop.call_soon(self._actual_callback)

    def _actual_callback(self):
        self._future = self.loop.create_task(self.run())
        self._future.add_done_callback(
            lambda future: self._schedule_callback)

    async def run(self):
        await self.callback(*self.args, **self.kwargs)

    def start(self, *args, **kwargs):
        assert (
            self.callback is not None
            or self.run is not Cycler.run
        ), 'callback is None and run is not overridden'

        self.args = args
        self.kwargs = kwargs
        self._schedule_callback(False)

    def stop(self):
        self.cancelled = True
        if self._handle is not None:
            self._handle.cancel()
        if self._task is not None:
            try:
                self._task.cancel()
            except asyncio.InvalidStateError:
                pass
