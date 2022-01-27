from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from .base_events import BaseEvent

if TYPE_CHECKING:
    from datetime import datetime

    from ..objects import (
        BaseChannel,
        ObjectWrapper,
    )
    from ..json import JSONData
    from ..websockets import Shard

__all__ = (
    'ChannelEvents',
    'BaseChannelEvent',
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


class BaseChannelEvent(BaseEvent):
    @property
    def guild(self) -> ObjectWrapper:
        return self.client.guilds.wrap_id(self.payload.get('guild_id'))


class ChannelCreateEvent(BaseChannelEvent):
    __slots__ = ('channel',)

    def __init__(self, *, shard: Shard, payload: JSONData, channel: BaseChannel) -> None:
        super().__init__(shard=shard, payload=payload)
        self.channel = channel

    def __repr__(self) -> str:
        return f'<ChannelCreateEvent channel={self.channel!r}>'


class ChannelUpdateEvent(BaseChannelEvent):
    __slots__ = ('channel',)

    def __init__(self, *, shard: Shard, payload: JSONData, channel: BaseChannel) -> None:
        super().__init__(shard=shard, payload=payload)
        self.channel = channel

    def __repr__(self) -> str:
        return f'<ChannelUpdateEvent channel={self.channel!r}>'


class ChannelDeleteEvent(BaseChannelEvent):
    __slots__ = ('channel',)

    def __init__(self, *, shard: Shard, payload: JSONData, channel: BaseChannel) -> None:
        super().__init__(shard=shard, payload=payload)
        self.channel = channel

    def __repr__(self) -> str:
        return f'<ChannelDeleteEvent channel={self.channel!r}>'


class ChannelPinsUpdateEvent(BaseChannelEvent):
    __slots__ = ('channel', 'timestamp')

    def __init__(
        self, *, shard: Shard, payload: JSONData, channel: ObjectWrapper, timestamp: datetime
    ) -> None:
        super().__init__(shard=shard, payload=payload)
        self.channel = channel
        self.timestamp = timestamp

    def __repr__(self) -> str:
        return f'<ChannelPinsUpdateEvent channel={self.channel!r} timestamp={self.timestamp!r}>'
