from __future__ import annotations

import asyncio
from numbers import Number
from typing import Any, Awaitable, Callable, ClassVar, Optional


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

    def close(self) -> None: ...


def ensure_future(coro: Awaitable[Any] | Any) -> Optional[asyncio.Future]: ...


class EventDispatcher:
    loop: Optional[asyncio.AbstractEventLoop]
    _listeners: dict[str, Callable[..., Any]]
    _waiters: dict[str, EventWaiter]
    _subscribers: list[EventDispatcher]
    events: ClassVar[EventNamespace]

    def __init__(self, loop: asyncio.AbstractEventLoop = ...) -> None: ...

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

    def on(self, name: Optional[str] = None) -> Callable[..., Any]: ...

    def once(self, name: Optional[str] = None) -> Callable[..., Any]: ...
    # TODO: -> Callable[Callable[Callable[Callable[]]]]
