from __future__ import annotations

import enum
from typing import Optional, TYPE_CHECKING

from .base_listener import (
    BaseWebSocketListener,
    WebSocketIntents,
)
from ...exceptions import UnknownModelError

if TYPE_CHECKING:
    from .base_listener import WaiterFilter
    from ...models import Guild
    from ...json import JSONData

__all__ = (
    'GuildEvent',
    'GuildListener',
    'GuildJoinEvent',
    'GuildAvailableEvent',
    'GuildReceiveEvent',
    'GuildUpdateEvent',
    'GuildDeleteEvent',
)


class GuildEvent(str, enum.Enum):
    JOIN = 'GUILD_JOIN'
    AVAILABLE = 'GUILD_AVAILABLE'
    RECEIVE = 'GUILD_RECEIVE'
    UPDATE = 'GUILD_UPDATE'
    DELETE = 'GUILD_DELETE'
    UNAVAILABLE = 'GUILD_UNAVAILABLE'


class GuildListener(BaseWebSocketListener):
    def get_event(self, name: str) -> GuildEvent:
        return GuildEvent(name)

    def get_intents(self) -> WebSocketIntents:
        return WebSocketIntents.GUILDS

    async def dispatch_guild_join(self, payload: JSONData) -> GuildJoinEvent:
        guild = await self.client.guilds.upsert(payload)
        return GuildJoinEvent(guild=guild, payload=payload)

    async def dispatch_guild_available(self, payload: JSONData) -> GuildAvailableEvent:
        guild = await self.client.guilds.upsert(payload)
        return GuildAvailableEvent(guild=guild, payload=payload)

    async def dispatch_guild_receive(self, payload: JSONData) -> GuildReceiveEvent:
        guild = await self.client.guilds.upsert(payload)
        return GuildReceiveEvent(guild=guild, payload=payload)

    async def dispatch_guild_update(self, payload: JSONData) -> GuildUpdateEvent:
        guild = await self.client.guilds.upsert(payload)
        return GuildUpdateEvent(guild=guild, payload=payload)

    async def dispatch_guild_delete_event(self, payload: JSONData) -> GuildDeleteEvent:
        try:
            guild = self.client.guilds.pop(payload['id'])
        except UnknownModelError:
            guild = None

        return GuildDeleteEvent(guild=guild, payload=payload)

    def wait_for_join(
        self, *, timeout: Optional[float] = None, filter: WaiterFilter[GuildJoinEvent] = None
    ):
        return self.create_waiter(GuildEvent.JOIN, timeout=timeout, filter=filter)

    def wait_for_available(
        self, *, timeout: Optional[float] = None, filter: WaiterFilter[GuildAvailableEvent] = None
    ):
        return self.create_waiter(GuildEvent.AVAILABLE, timeout=timeout, filter=filter)

    def wait_for_receive(
        self, *, timeout: Optional[float] = None, filter: WaiterFilter[GuildReceiveEvent] = None
    ):
        return self.create_waiter(GuildEvent.RECEIVE, timeout=timeout, filter=filter)

    def wait_for_update(
        self, *, timeout: Optional[float] = None, filter: WaiterFilter[GuildUpdateEvent] = None
    ):
        return self.create_waiter(GuildEvent.UPDATE, timeout=timeout, filter=filter)

    def wait_for_delete(
        self, *, timeout: Optional[float] = None, filter: WaiterFilter[GuildDeleteEvent] = None
    ):
        return self.create_waiter(GuildEvent.DELETE, timeout=timeout, filter=filter)


class GuildJoinEvent:
    __slots__ = ('guild', 'payload')

    def __init__(self, *, guild: Guild, payload: JSONData) -> None:
        self.guild = guild
        self.payload = payload

    def __repr__(self) -> str:
        return f'GuildJoinEvent(guild={self.guild!r})'


class GuildAvailableEvent:
    __slots__ = ('guild', 'payload')

    def __init__(self, *, guild: Guild, payload: JSONData) -> None:
        self.guild = guild
        self.payload = payload

    def __repr__(self) -> str:
        return f'GuildAvailableEvent(guild={self.guild!r})'


class GuildReceiveEvent:
    __slots__ = ('guild', 'payload')

    def __init__(self, *, guild: Guild, payload: JSONData) -> None:
        self.guild = guild
        self.payload = payload

    def __repr__(self) -> str:
        return f'GuildReceiveEvent(guild={self.guild!r})'


class GuildUpdateEvent:
    __slots__ = ('guild', 'payload')

    def __init__(self, *, guild: Guild, payload: JSONData) -> None:
        self.guild = guild
        self.payload = payload

    def __repr__(self) -> str:
        return f'GuildUpdateEvent(guild={self.guild!r})'


class GuildDeleteEvent:
    __slots__ = ('guild',)

    def __init__(self, *, guild: Guild, payload: JSONData) -> None:
        self.guild = guild
        self.payload = payload

    def __repr__(self) -> str:
        return f'GuildDeleteEvent(guild={self.guild!r})'
