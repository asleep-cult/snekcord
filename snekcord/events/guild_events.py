import enum
from typing import TYPE_CHECKING

from .base_events import BaseEvent

if TYPE_CHECKING:
    from ..objects import Guild
    from ..json import JSONData
    from ..websockets import ShardWebSocket


class GuildEventType(str, enum.Enum):
    JOIN = 'GUILD_JOIN'
    AVAILABLE = 'GUILD_AVAILABLE'
    RECEIVE = 'GUILD_RECEIVE'
    UPDATE = 'GUILD_UPDATE'
    DELETE = 'GUILD_DELETE'
    UNAVAILABLE = 'GUILD_UNAVAILABLE'


class GuildJoinEvent(BaseEvent):
    __slots__ = ('guild',)

    def __init__(
        self, *, shard: ShardWebSocket, payload: JSONData, guild: Guild
    ) -> None:
        super().__init__(shard=shard, payload=payload)
        self.guild = guild

    @property
    def type(self) -> GuildEventType:
        return GuildEventType.JOIN

    def __repr__(self) -> str:
        return f'<GuildJoinEvent guild={self.guild!r}>'


class GuildAvailableEvent(BaseEvent):
    __slots__ = ('guild',)

    def __init__(
        self, *, shard: ShardWebSocket, payload: JSONData, guild: Guild
    ) -> None:
        super().__init__(shard=shard, payload=payload)
        self.guild = guild

    @property
    def type(self) -> GuildEventType:
        return GuildEventType.AVAILABLE

    def __repr__(self) -> str:
        return f'<GuildAvailableEvent guild={self.guild!r}>'


class GuildReceiveEvent(BaseEvent):
    __slots__ = ('guild',)

    def __init__(
        self, *, shard: ShardWebSocket, payload: JSONData, guild: Guild
    ) -> None:
        super().__init__(shard=shard, payload=payload)
        self.guild = guild

    @property
    def type(self) -> GuildEventType:
        return GuildEventType.RECEIVE

    def __repr__(self) -> str:
        return f'<GuildReceiveEvent guild={self.guild!r}>'


class GuildUpdateEvent(BaseEvent):
    __slots__ = ('guild',)

    def __init__(
        self, *, shard: ShardWebSocket, payload: JSONData, guild: Guild
    ) -> None:
        super().__init__(shard=shard, payload=payload)
        self.guild = guild

    @property
    def type(self) -> GuildEventType:
        return GuildEventType.UPDATE

    def __repr__(self) -> str:
        return f'<GuildUpdateEvent guild={self.guild!r}>'


class GuildDeleteEvent(BaseEvent):
    __slots__ = ('guild',)

    def __init__(
        self, *, shard: ShardWebSocket, payload: JSONData, guild: Guild
    ) -> None:
        super().__init__(shard=shard, payload=payload)
        self.guild = guild

    @property
    def type(self) -> GuildEventType:
        return GuildEventType.DELETE

    def __repr__(self) -> str:
        return f'<GuildDeleteEvent guild={self.guild!r}>'


class GuildUnavailableEvent(BaseEvent):
    __slots__ = ('guild',)

    def __init__(
        self, *, shard: ShardWebSocket, payload: JSONData, guild: Guild
    ) -> None:
        super().__init__(shard=shard, payload=payload)
        self.guild = guild

    @property
    def type(self) -> GuildEventType:
        return GuildEventType.UNAVAILABLE

    def __repr__(self) -> str:
        return f'<GuildUnavailableEvent guild={self.guild!r}>'
