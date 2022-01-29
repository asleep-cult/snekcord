from __future__ import annotations

import enum
import typing

import attr

from .base_events import BaseEvent

if typing.TYPE_CHECKING:
    from ..objects import Guild

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


@attr.s(kw_only=True)
class GuildJoinEvent(BaseEvent):
    guild: Guild = attr.ib()


@attr.s(kw_only=True)
class GuildAvailableEvent(BaseEvent):
    guild: Guild = attr.ib()


@attr.s(kw_only=True)
class GuildReceiveEvent(BaseEvent):
    guild: Guild = attr.ib()


@attr.s(kw_only=True)
class GuildUpdateEvent(BaseEvent):
    guild: Guild = attr.ib()


class GuildDeleteEvent(BaseEvent):
    guild: typing.Optional[Guild] = attr.ib()


class GuildUnavailableEvent(BaseEvent):
    guild: typing.Optional[Guild] = attr.ib()
