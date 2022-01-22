from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from .base_events import BaseEvent

if TYPE_CHECKING:
    from ..objects import Guild
    from ..json import JSONData
    from ..websockets import Shard

__all__ = (
    'GuildEvents',
    'GuildJoinEvent',
    'GuildAvailableEvent',
    'GuildReceiveEvent',
    'GuildUpdateEvent',
    'GuildDeleteEvent',
    'GuildUnavailableEvent',
)


class GuildEvents(str, enum.Enum):
    JOIN = 'GUILD_JOIN'
    AVAILABLE = 'GUILD_AVAILABLE'
    RECEIVE = 'GUILD_RECEIVE'
    UPDATE = 'GUILD_UPDATE'
    DELETE = 'GUILD_DELETE'
    UNAVAILABLE = 'GUILD_UNAVAILABLE'


class GuildJoinEvent(BaseEvent):
    __slots__ = ('guild',)

    def __init__(self, *, shard: Shard, payload: JSONData, guild: Guild) -> None:
        super().__init__(shard=shard, payload=payload)
        self.guild = guild

    def __repr__(self) -> str:
        return f'<GuildJoinEvent guild={self.guild!r}>'


class GuildAvailableEvent(BaseEvent):
    __slots__ = ('guild',)

    def __init__(self, *, shard: Shard, payload: JSONData, guild: Guild) -> None:
        super().__init__(shard=shard, payload=payload)
        self.guild = guild

    def __repr__(self) -> str:
        return f'<GuildAvailableEvent guild={self.guild!r}>'


class GuildReceiveEvent(BaseEvent):
    __slots__ = ('guild',)

    def __init__(self, *, shard: Shard, payload: JSONData, guild: Guild) -> None:
        super().__init__(shard=shard, payload=payload)
        self.guild = guild

    def __repr__(self) -> str:
        return f'<GuildReceiveEvent guild={self.guild!r}>'


class GuildUpdateEvent(BaseEvent):
    __slots__ = ('guild',)

    def __init__(self, *, shard: Shard, payload: JSONData, guild: Guild) -> None:
        super().__init__(shard=shard, payload=payload)
        self.guild = guild

    def __repr__(self) -> str:
        return f'<GuildUpdateEvent guild={self.guild!r}>'


class GuildDeleteEvent(BaseEvent):
    __slots__ = ('guild',)

    def __init__(self, *, shard: Shard, payload: JSONData, guild: Guild) -> None:
        super().__init__(shard=shard, payload=payload)
        self.guild = guild

    def __repr__(self) -> str:
        return f'<GuildDeleteEvent guild={self.guild!r}>'


class GuildUnavailableEvent(BaseEvent):
    __slots__ = ('guild',)

    def __init__(self, *, shard: Shard, payload: JSONData, guild: Guild) -> None:
        super().__init__(shard=shard, payload=payload)
        self.guild = guild

    def __repr__(self) -> str:
        return f'<GuildUnavailableEvent guild={self.guild!r}>'
