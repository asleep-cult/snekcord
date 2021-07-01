from __future__ import annotations

import asyncio
import typing as t

from ..enums import Enum
from ..clients.wsclient import WebSocketClient, WebSocketIntents
from ..objects.userobject import User
from ..typedefs import Json, SnowflakeConvertible

__all__ = ('ShardOpcode', 'ShardCloseCode', 'Shard', 'ShardWebSocket')


class ShardOpcode(Enum[int]):
    DISPATCH: t.ClassVar[int]
    HEARTBEAT: t.ClassVar[int]
    IDENTIFY: t.ClassVar[int]
    PRESENCE_UPDATE: t.ClassVar[int]
    VOICE_STATE_UPDATE: t.ClassVar[int]
    VOICE_SERVER_PING: t.ClassVar[int]
    RESUME: t.ClassVar[int]
    RECONNECT: t.ClassVar[int]
    REQUEST_GUILD_MEMBERS: t.ClassVar[int]
    INVALID_SESSION: t.ClassVar[int]
    HELLO: t.ClassVar[int]
    HEARTBEAT_ACK: t.ClassVar[int]


class ShardCloseCode(Enum[int]):
    UNKNOWN_ERROR: t.ClassVar[int]
    UNKNOWN_OPCODE: t.ClassVar[int]
    DECODE_ERROR: t.ClassVar[int]
    NOT_AUTHENTICATED: t.ClassVar[int]
    AUTHENTICATION_FAILED: t.ClassVar[int]
    ALREADY_AUTHENTICATED: t.ClassVar[int]
    INVALID_SEQUENCE: t.ClassVar[int]
    RATE_LIMITED: t.ClassVar[int]
    SESSION_TIMED_OUT: t.ClassVar[int]
    INVALID_SHARD: t.ClassVar[int]
    SHARDING_REQUIRED: t.ClassVar[int]
    INVALID_API_VERSION: t.ClassVar[int]
    INVALID_INTENTS: t.ClassVar[int]
    DISALLOWED_INTENTS: t.ClassVar[int]


class ShardWebSocketCallbacks:
    HELLO: t.Callable[[], None]
    READY: t.Callable[[Json], None]
    DISPATCH: t.Callable[[str, Json], None]
    GUILDS_RECEIVED: t.Callable[[], None]
    CLOSED: t.Callable[[int, Json], None]
    CLOSING: t.Callable[[BaseException], None]
    CONNECTION_LOST: t.Callable[[BaseException], None]


class Shard:
    client: WebSocketClient
    id: int
    count: int
    loop: asyncio.AbstractEventLoop
    token: str
    intents: WebSocketIntents
    callbacks: ShardWebSocketCallbacks
    session_id: int
    sequence: int
    available_guilds: set[str]
    unavailable_guilds: set[str]
    heartbeater_task: asyncio.Task[t.NoReturn] | None
    user: User | None
    ws: ShardWebSocket

    def __init__(self, client: WebSocketClient, shard_id: int) -> None: ...

    def create_ws(self, *, reconnect: bool = ...) -> None: ...

    @property
    def latency(self) -> float: ...

    async def on_hello(self) -> None: ...

    async def on_ready(self, data: Json) -> None: ...

    async def on_dispatch(self, name: str, data: Json) -> None: ...

    async def on_guilds_received(self) -> None: ...

    async def on_closed(self, code: int, data: Json) -> None: ...

    async def on_closing(self, exc: BaseException) -> None: ...

    async def on_connection_lost(self, exc: BaseException) -> None: ...

    async def heartbeater(self) -> t.NoReturn: ...

    async def connect(self, *args: t.Any, **kwargs: t.Any) -> None: ...


class ShardWebSocket:
    id: int
    count: int
    token: str
    intents: WebSocketIntents | None
    callbacks: ShardWebSocketCallbacks
    v: str | None
    info: tuple[int, int] | None
    session_id: str | None
    startup_guilds: set[str]
    unavailable_guilds: set[str]
    available_guilds: set[str]
    sequence: int

    def __init__(self, shard_id: int, shard_count: int, *,
                 loop: asyncio.AbstractEventLoop | None = ...,
                 token: str, intents: WebSocketIntents | None,
                 callbacks: ShardWebSocketCallbacks,
                 session_id: str | None = ...,
                 available_guilds: set[str] | None = ...,
                 unavailable_guilds: set[str] | None = ...,
                 sequence: int = ...) -> None: ...

    @property
    def shard(self) -> tuple[int, int] | None: ...

    async def identify(self) -> None: ...

    async def resume(self) -> None: ...

    async def request_guild_members(
        self, guild: SnowflakeConvertible,
        presences: bool | None = ..., limit: int | None = ...,
        users: t.Iterable[SnowflakeConvertible] | None = ...,
        query: str | None = ...) -> None: ...
