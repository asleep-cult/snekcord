import enum
from typing import TYPE_CHECKING

from .base_events import BaseEvent

if TYPE_CHECKING:
    from datetime import datetime

    from ..objects import BaseChannel
    from ..json import JSONData
    from ..websockets import ShardWebSocket


class ChannelEventType(str, enum.Enum):
    CREATE = 'CHANNEL_DELETE'
    UPDATE = 'CHANNEL_UPDATE'
    DELETE = 'CHANNEL_DELETE'
    PINS_UPDATE = 'CHANNEL_PINS_UPDATE'


class ChannelCreateEvent(BaseEvent):
    __slots__ = ('channel',)

    def __init__(self, *, shard: ShardWebSocket, payload: JSONData, channel: BaseChannel) -> None:
        super().__init__(shard=shard, payload=payload)
        self.channel = channel

    @property
    def type(self) -> ChannelEventType:
        return ChannelEventType.CREATE

    def __repr__(self) -> str:
        return f'<ChannelCreateEvent channel={self.channel!r}>'


class ChannelUpdateEvent(BaseEvent):
    __slots__ = ('channel',)

    def __init__(self, *, shard: ShardWebSocket, payload: JSONData, channel: BaseChannel) -> None:
        super().__init__(shard=shard, payload=payload)
        self.channel = channel

    @property
    def type(self) -> ChannelEventType:
        return ChannelEventType.UPDATE

    def __repr__(self) -> str:
        return f'<ChannelUpdateEvent channel={self.channel!r}>'


class ChannelDeleteEvent(BaseEvent):
    __slots__ = ('channel',)

    def __init__(self, *, shard: ShardWebSocket, payload: JSONData, channel: BaseChannel) -> None:
        super().__init__(shard=shard, payload=payload)
        self.channel = channel

    @property
    def type(self) -> ChannelEventType:
        return ChannelEventType.DELETE

    def __repr__(self) -> str:
        return f'<ChannelDeleteEvent channel={self.channel!r}>'


class ChannelPinsUpdateEvent(BaseEvent):
    __slots__ = ('channel', 'timestamp')

    def __init__(
        self, *, shard: ShardWebSocket, payload: JSONData, channel: BaseChannel, timestamp: datetime
    ) -> None:
        super().__init__(shard=shard, payload=payload)
        self.channel = channel
        self.timestamp = timestamp

    @property
    def type(self) -> ChannelEventType:
        return ChannelEventType.PINS_UPDATE

    def __repr__(self) -> str:
        return f'<ChannelPinsUpdateEvent channel={self.channel!r} timestamp={self.timestamp!r}>'
