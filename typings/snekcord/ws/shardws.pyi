import enum
from typing import Any, Iterable, Literal, Optional, Set, SupportsInt, Union

from .basews import BaseWebSocket, WebSocketWorker
from ..objects.baseobject import BaseObject
from ..objects.userobject import User
from ..utils import Snowflake

_ConvertableToInt = Union[SupportsInt, str]
_SnowflakeType = Union[BaseObject[Snowflake], _ConvertableToInt]

class ShardOpcode(enum.IntEnum):
    DISPATCH: Literal[0]
    HEARTBEAT: Literal[1]
    IDENTIFY: Literal[2]
    PRESENCE_UPDATE: Literal[3]
    VOICE_STATE_UPDATE: Literal[4]
    VOICE_SERVER_PING: Literal[5]
    RESUME: Literal[6]
    RECONNECT: Literal[7]
    REQUEST_GUILD_MEMBERS: Literal[8]
    INVALID_SESSION: Literal[9]
    HELLO: Literal[10]
    HEARTBEAT_ACK: Literal[11]

class ShardCloseCode(enum.IntEnum):
    UNKNOWN_ERROR: Literal[4000]
    UNKNOWN_OPCODE: Literal[4001]
    DECODE_ERROR: Literal[4002]
    NOT_AUTHENTICATED: Literal[4003]
    AUTHENTICATION_FAILED: Literal[4004]
    ALREADY_AUTHENTICATED: Literal[4005]
    INVALID_SEQUENCE: Literal[4007]
    RATE_LIMITED: Literal[4008]
    SESSION_TIMED_OUT: Literal[4009]
    INVALID_SHARD: Literal[4010]
    SHARDING_REQUIRED: Literal[4011]
    INVALID_API_VERSION: Literal[4012]
    INVALID_INTENTS: Literal[4013]
    DISALLOWED_INTENTS: Literal[4014]

class Shard(BaseWebSocket):
    worker: WebSocketWorker
    id: int
    intents: int
    v: Optional[str]
    user: Optional[User]
    startup_guilds: Set[int]
    available_guilds: Set[int]
    unavailable_guilds: Set[int]
    session_id: Optional[int]
    info: Any
    sequence: int
    _chunk_nonce: int

    def __init__(
        self, worker: WebSocketWorker, shard_id: Optional[int] = ..., intents: Optional[int] = ...
    ) -> None: ...

    def _remove_startup_guild(self, guild_id: int) -> None: ...
    async def identify(self) -> None: ...
    async def resume(self) -> None: ...
    async def send_heartbeat(self) -> None: ...
    async def request_guild_members(
        self, guild: _SnowflakeType, presences: Any = ..., limit: Optional[float] = ...,
        users: Optional[Iterable[_SnowflakeType]] = ..., query: Optional[str] = ...
    ) -> None: ...
    async def ws_text_received(self, data: Any) -> None: ...