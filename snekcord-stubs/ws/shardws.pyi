from __future__ import annotations

import asyncio
import typing as t

from ..clients.wsclient import WebSocketClient, WebSocketIntents
from ..objects.userobject import User
from ..typedefs import Json, SnowflakeConvertible
from ..utils.enum import Enum

__all__ = ('ShardOpcode', 'ShardCloseCode', 'Shard', 'ShardWebSocket')


class ShardOpcode(Enum[int]):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    VOICE_SERVER_PING = 5
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11


class ShardCloseCode(Enum[int]):
    UNKNOWN_ERROR = 4000
    UNKNOWN_OPCODE = 4001
    DECODE_ERROR = 4002
    NOT_AUTHENTICATED = 4003
    AUTHENTICATION_FAILED = 4004
    ALREADY_AUTHENTICATED = 4005
    INVALID_SEQUENCE = 4007
    RATE_LIMITED = 4008
    SESSION_TIMED_OUT = 4009
    INVALID_SHARD = 4010
    SHARDING_REQUIRED = 4011
    INVALID_API_VERSION = 4012
    INVALID_INTENTS = 4013
    DISALLOWED_INTENTS = 4014


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
