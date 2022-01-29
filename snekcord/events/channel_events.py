from __future__ import annotations

import enum
import typing

import attr

from .base_events import BaseEvent

if typing.TYPE_CHECKING:
    from datetime import datetime

    from ..objects import BaseChannel
    from ..states import GuildIDWrapper

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
class ChannelCreateEvent(BaseEvent):
    guild: GuildIDWrapper = attr.ib()
    channel: BaseChannel = attr.ib()


@attr.s(kw_only=True)
class ChannelUpdateEvent(BaseEvent):
    guild: GuildIDWrapper = attr.ib()
    channel: BaseChannel = attr.ib()


@attr.s(kw_only=True)
class ChannelDeleteEvent(BaseEvent):
    guild: GuildIDWrapper = attr.ib()
    channel: typing.Optional[BaseChannel] = attr.ib()


class ChannelPinsUpdateEvent(BaseEvent):
    guild: GuildIDWrapper = attr.ib()
    channel: typing.Optional[BaseChannel] = attr.ib()
    timestamp: datetime
