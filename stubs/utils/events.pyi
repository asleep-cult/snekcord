from __future__ import annotations

import asyncio
from numbers import Number
from typing import Any, Awaitable, Callable, ClassVar, Generator, Optional,     TypeVar

T = TypeVar('T')

class EventDefinition:
    pass


class EventNamespace:
    __events__: ClassVar[dict[str, EventDefinition]]


class EventWaiter:
    name: str
    dispatcher: EventDispatcher
    timeout: Optional[Number]
    filterer: Optional[Callable[..., bool]]
    _queue: asyncio.Queue[tuple[Any, ...]]

    def __init__(self, name: str, dispatcher: EventDispatcher,
                 timeout: Optional[Number] = ...,
                 filterer: Optional[Callable[..., bool]] = ...) -> None: ...

    def _put(self, value: Any) -> None: ...

    async def _get(self) -> Any: ...

    def __aiter__(self: T) -> T: ...

    async def __anext__(self) -> tuple[Any, ...]: ...

    async def __await__impl(self) -> tuple[Any, ...]: ...

    def __await__(self) -> Generator[Optional[asyncio.Future], None, tuple[Any, ...]]: ...

    def close(self) -> None: ...

    __del__ = close


def ensure_future(coro: Awaitable[Any] | Any) -> Optional[asyncio.Future]: ...


class EventDispatcher:
    loop: Optional[asyncio.AbstractEventLoop]
    _listeners: dict[str, Callable[..., Any]]
    _waiters: dict[str, EventWaiter]
    _subscribers: list[EventDispatcher]
    events: ClassVar[EventNamespace]

    def __init__(self, *, loop: Optional[asyncio.AbstractEventLoop] = ...) -> None: ...

    def register_listener(self, name: str,
                          callback: Callable[..., Any]) -> None: ...

    def remove_listener(self, name: str,
                        callback: Callable[..., Any]) -> None: ...

    def register_waiter(self, *args: Any,
                        **kwargs: Any) -> EventWaiter: ...

    wait = register_waiter

    def remove_waiter(self, waiter: EventWaiter) -> None: ...

    def run_callbacks(self, name: str, *args: Any) -> None: ...

    def dispatch(self, name: str, *args: Any) -> None: ...

    def subscribe(self, dispatcher: EventDispatcher) -> None: ...

    def unsubscribe(self, dispatcher: EventDispatcher) -> None: ...

    def on(self, name: Optional[str] = None) -> Callable[[Callable[..., T]], Callable[..., T]]: ...

    def once(self, name: Optional[str] = None) -> Callable[[Callable[..., T]], Callable[..., T]]: ...
