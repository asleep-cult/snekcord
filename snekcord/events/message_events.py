from __future__ import annotations

import enum
import typing

import attr

from .base_events import BaseEvent

if typing.TYPE_CHECKING:
    from ..objects import Message
    from ..states import ChannelIDWrapper, GuildIDWrapper

__all__ = (
    'MessageEvents',
    'MessageCreateEvent',
    'MessageUpdateEvent',
    'MessageDeleteEvent',
    'MessageBulkDeleteEvent',
)


class MessageEvents(str, enum.Enum):
    CREATE = 'MESSAGE_CREATE'
    UPDATE = 'MESSAGE_UPDATE'
    DELETE = 'MESSAGE_DELETE'
    BULK_DELETE = 'MESSAGE_DELETE_BULK'


@attr.s(kw_only=True)
class MessageCreateEvent(BaseEvent):
    guild: GuildIDWrapper = attr.ib()
    channel: ChannelIDWrapper = attr.ib()
    message: Message = attr.ib()


@attr.s(kw_only=True)
class MessageUpdateEvent(BaseEvent):
    guild: GuildIDWrapper = attr.ib()
    channel: ChannelIDWrapper = attr.ib()
    message: Message = attr.ib()


@attr.s(kw_only=True)
class MessageDeleteEvent(BaseEvent):
    guild: GuildIDWrapper = attr.ib()
    channel: ChannelIDWrapper = attr.ib()
    message: typing.Optional[Message] = attr.ib()


@attr.s(kw_only=True)
class MessageBulkDeleteEvent(BaseEvent):
    guild: GuildIDWrapper = attr.ib()
    channel: ChannelIDWrapper = attr.ib()
    messages: typing.List[Message] = attr.ib()
