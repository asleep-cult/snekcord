from __future__ import annotations

import enum

from .base_listener import (
    BaseWebSocketListener,
    WebSocketIntents,
)
from ...exceptions import UnknownModelError

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
    def to_event(self, name):
        return GuildEvent(name)

    def get_intents(self):
        return WebSocketIntents.GUILDS

    def wait_for_join(self, *, timeout=None, filter=None):
        return self.create_waiter(GuildEvent.JOIN, timeout=timeout, filter=filter)

    def wait_for_available(self, *, timeout=None, filter=None):
        return self.create_waiter(GuildEvent.AVAILABLE, timeout=timeout, filter=filter)

    def wait_for_receive(self, *, timeout=None, filter=None):
        return self.create_waiter(GuildEvent.RECEIVE, timeout=timeout, filter=filter)

    def wait_for_update(self, *, timeout=None, filter=None):
        return self.create_waiter(GuildEvent.UPDATE, timeout=timeout, filter=filter)

    def wait_for_delete(self, *, timeout=None, filter=None):
        return self.create_waiter(GuildEvent.DELETE, timeout=timeout, filter=filter)

    def wait_for_unavailable(self, *, timeout=None, filter=None):
        return self.create_waiter(GuildEvent.UNAVAILABLE, timeout=timeout, filter=filter)


class _GuildUpsertEvent:
    __slots__ = ('guild', 'payload')

    def __init__(self, *, guild, payload):
        self.guild = guild
        self.payload = payload

    @classmethod
    async def execute(cls, client, payload):
        guild = await client.guilds.upsert(payload)
        return cls(guild=guild, payload=payload)


@GuildListener.event(GuildEvent.JOIN)
class GuildJoinEvent(_GuildUpsertEvent):
    __slots__ = ()

    def __repr__(self):
        return f'GuildJoinEvent(guild={self.guild!r})'


@GuildListener.event(GuildEvent.AVAILABLE)
class GuildAvailableEvent(_GuildUpsertEvent):
    __slots__ = ()

    def __repr__(self):
        return f'GuildAvailableEvent(guild={self.guild!r})'


@GuildListener.event(GuildEvent.RECEIVE)
class GuildReceiveEvent(_GuildUpsertEvent):
    __slots__ = ()

    def __repr__(self):
        return f'GuildReceiveEvent(guild={self.guild!r})'


@GuildListener.event(GuildEvent.UPDATE)
class GuildUpdateEvent(_GuildUpsertEvent):
    __slots__ = ()

    def __repr__(self):
        return f'GuildCUpdateEvent(guild={self.guild!r})'


@GuildListener.event(GuildEvent.DELETE)
class GuildDeleteEvent:
    __slots__ = ('guild',)

    def __init__(self, *, guild):
        self.guild = guild

    def __repr__(self):
        return f'GuildDeleteEvent(guild={self.guild!r})'

    @classmethod
    async def execute(cls, client, data):
        try:
            guild = client.guilds.pop(data['id'])
        except UnknownModelError:
            guild = None

        return cls(guild=guild)
