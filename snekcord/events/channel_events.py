from __future__ import annotations

import enum
import typing

import attr

from ..api import (
    RawChannelCreate,
    RawChannelDelete,
    RawChannelPinsUpdate,
    RawChannelUpdate,
)
from .base_events import BaseEvent

if typing.TYPE_CHECKING:
    from datetime import datetime

    from ..objects import Channel, ChannelIDWrapper, GuildIDWrapper
    from ..undefined import MaybeUndefined

__all__ = (
    'ChannelEvents',
    'BaseEvent',
    'ChannelCreateEvent',
    'ChannelUpdateEvent',
    'ChannelDeleteEvent',
    'ChannelPinsUpdateEvent',
)


class ChannelEvents(str, enum.Enum):
    CREATE = 'CHANNEL_DELETE'
    UPDATE = 'CHANNEL_UPDATE'
    DELETE = 'CHANNEL_DELETE'
    PINS_UPDATE = 'CHANNEL_PINS_UPDATE'


@attr.s(kw_only=True)
class ChannelCreateEvent(BaseEvent[RawChannelCreate]):
    guild: GuildIDWrapper = attr.ib()
    channel: Channel = attr.ib()


@attr.s(kw_only=True)
class ChannelUpdateEvent(BaseEvent[RawChannelUpdate]):
    guild: GuildIDWrapper = attr.ib()
    channel: Channel = attr.ib()


@attr.s(kw_only=True)
class ChannelDeleteEvent(BaseEvent[RawChannelDelete]):
    guild: GuildIDWrapper = attr.ib()
    channel: typing.Optional[Channel] = attr.ib()


@attr.s(kw_only=True)
class ChannelPinsUpdateEvent(BaseEvent[RawChannelPinsUpdate]):
    guild: GuildIDWrapper = attr.ib()
    channel: ChannelIDWrapper = attr.ib()
    timestamp: MaybeUndefined[typing.Optional[datetime]] = attr.ib()
