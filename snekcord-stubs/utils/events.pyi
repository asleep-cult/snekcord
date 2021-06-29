from __future__ import annotations

import asyncio
import typing as t
from weakref import WeakSet

from typing_extensions import ParamSpec

from ..typedefs import AnyCallable, AnyCoroCallable

__all__ = ('EventWaiter', 'EventDispatcher',)

T = t.TypeVar('T')
P = ParamSpec('P')


class EventWaiter:
    name: str
    dispatcher: EventDispatcher
    timeout: float | None
    filter: AnyCallable | None

    def __init__(self, name: str, *, dispatcher: EventDispatcher,
                 timeout: float | None = ...,
                 filter: AnyCallable | None = ...) -> None: ...

    def close(self) -> None: ...


def ensure_future(coro: t.Any) -> asyncio.Future[t.Any] | None: ...


class EventDispatcher:
    __events__: t.ClassVar[dict[str, AnyCoroCallable] | None]

    loop: asyncio.AbstractEventLoop
    listeners: dict[str, list[AnyCallable]]
    waiters: dict[str, WeakSet[EventWaiter]]
    subscribers: list[EventDispatcher]

    def __init__(self, *, loop: asyncio.AbstractEventLoop | None = ...
                 ) -> None: ...

    def register_listener(self, name: str, callback: AnyCallable) -> None: ...

    def remove_listener(self, name: str, callback: AnyCallable) -> None: ...

    def register_waiter(self, *args: t.Any,
                        **kwargs: t.Any) -> EventWaiter: ...

    wait = register_waiter

    def remove_waiter(self, waiter: EventWaiter) -> None: ...

    def run_callbacks(self, name: str, *args: t.Any) -> None: ...

    async def dispatch(self, name: str, *args: t.Any) -> None: ...

    def subscribe(self, dispatcher: EventDispatcher) -> None: ...

    def unsubscribe(self, dispatcher: EventDispatcher) -> None: ...

    def on(self, name: str | None = ...) -> t.Callable[[t.Callable[P, T]],
                                                       t.Callable[P, T]]: ...

    def once(self, name: str | None = ...) -> t.Callable[[t.Callable[P, T]],
                                                         t.Callable[P, T]]: ...
