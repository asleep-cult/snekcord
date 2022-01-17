from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from .base_events import BaseEvent

if TYPE_CHECKING:
    from ..collection import Collection
    from ..json import JSONData
    from ..objects import (
        Message,
        ObjectWrapper,
    )
    from ..websockets import ShardWebSocket

__all__ = (
    'MessageEvent',
    'BaseMessageEvent',
    'MessageCreateEvent',
    'MessageUpdateEvent',
    'MessageDeleteEvent',
    'MessageBulkDeleteEvent',
)


class MessageEvent(str, enum.Enum):
    CREATE = 'MESSAGE_CREATE'
    UPDATE = 'MESSAGE_UPDATE'
    DELETE = 'MESSAGE_DELETE'
    BULK_DELETE = 'MESSAGE_DELETE_BULK'


class BaseMessageEvent(BaseEvent):
    @property
    def guild(self) -> ObjectWrapper:
        return self.client.guilds.wrap_id(self.payload.get('guild_id'))

    @property
    def channel(self) -> ObjectWrapper:
        return self.client.guilds.wrap_id(self.payload.get('channel_id'))


class MessageCreateEvent(BaseEvent):
    __slots__ = ('message',)

    def __init__(self, *, shard: ShardWebSocket, payload: JSONData, message: Message) -> None:
        super().__init__(shard=shard, payload=payload)
        self.message = message

    @staticmethod
    def get_type() -> MessageEvent:
        return MessageEvent.CREATE

    def __repr__(self) -> str:
        return f'<MessageCreateEvent message={self.message!r}>'


class MessageUpdateEvent(BaseEvent):
    __slots__ = ('message',)

    def __init__(self, *, shard: ShardWebSocket, payload: JSONData, message: Message) -> None:
        super().__init__(shard=shard, payload=payload)
        self.message = message

    @staticmethod
    def get_type() -> MessageEvent:
        return MessageEvent.UPDATE

    def __repr__(self) -> str:
        return f'<MessageUpdateEvent message={self.message!r}>'


class MessageDeleteEvent(BaseEvent):
    __slots__ = ('message',)

    def __init__(self, *, shard: ShardWebSocket, payload: JSONData, message: Message) -> None:
        super().__init__(shard=shard, payload=payload)
        self.message = message

    @staticmethod
    def get_type() -> MessageEvent:
        return MessageEvent.UPDATE

    def __repr__(self) -> str:
        return f'<MessageDeleteEvent message={self.message!r}>'


class MessageBulkDeleteEvent(BaseEvent):
    __slots__ = ('messages',)

    def __init__(self, *, shard: ShardWebSocket, payload: JSONData, messages: Collection) -> None:
        super().__init__(shard=shard, payload=payload)
        self.messages = messages

    @staticmethod
    def get_type() -> MessageEvent:
        return MessageEvent.UPDATE

    def __repr__(self) -> str:
        return f'<MessageBulkDeleteEvent messages={self.messages!r}>'
