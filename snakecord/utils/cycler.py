import asyncio
from numbers import Number
from typing import Any, Callable, Optional

__all__ = ('Cycler',)


class Cycler:
    """A class that runs a coroutine every `delay` seconds.

    Attributes
        loop: Optional[asyncio.AbstractEventLoop]
            The event loop to use when creating the task,
            if None is provided :func:`asyncio.get_event_loop` is used.

        delay: Number
            The amount of time to wait between cycles (in seconds).

        callback: Optional[Callable[..., Any]]
            The coroutine to run, if None is provided
            :meth:`Cycler.run` must be overridden.
    """
    def __init__(self, *, loop: Optional[asyncio.AbstractEventLoop] = None,
                 delay: Number, callback: Optional[Callable[..., Any]] = None):
        if loop is not None:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()

        self.delay = delay
        self.callback = callback
        self.cancelled = False
        self._task = None
        self._handle = None

    def _schedule_callback(self, delay: bool = True) -> None:
        if not self.cancelled:
            if delay:
                self._handle = self.loop.call_later(
                    self.delay, self._actual_callback)
            else:
                self.loop.call_soon(self._actual_callback)

    def _actual_callback(self) -> None:
        self._future = self.loop.create_task(self.run())
        self._future.add_done_callback(
            lambda future: self._schedule_callback)

    async def run(self) -> None:
        """Called every cycle, can be overridden in a subclass."""
        await self.callback(*self.args, **self.kwargs)

    def start(self, *args, **kwargs) -> None:
        r"""Starts the :class:`Cycler`, the first cycle will happen
        immediately.

        Args:
            \*args: Any
                The arguments to use when calling the callback.

            \*\*kwargs: Any
                The keyword arguments to use when calling the
                callback.

        Raises:
            :exc:`AssertionError`:
                Raised when :attr:`Cycler.callback` is None
                and :meth:`Cycler.run` is not overridden.
        """
        assert (
            self.callback is not None
            or self.run is not Cycler.run
        ), 'callback is None and run is not overridden'

        self.args = args
        self.kwargs = kwargs
        self._schedule_callback(False)

    def stop(self) -> None:
        """Stops the :class:`Cycler`, cancelling the on-going task if any."""
        self.cancelled = True
        if self._handle is not None:
            self._handle.cancel()
        if self._task is not None:
            try:
                self._task.cancel()
            except asyncio.InvalidStateError:
                pass
