from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from .base_listener import (
    BaseWebSocketListener,
    WebSocketIntents,
)
from ...exceptions import UnknownModelError

if TYPE_CHECKING:
    from .base_listener import WaiterFilter
    from ...models import BaseChannel, ModelWrapper
    from ...json import JSONData
    from ..websocket_client import WebSocketClient

__all__ = (
    'ChannelEvent',
    'ChannelListener',
    'ChannelCreateEvent',
    'ChannelUpdateEvent',
    'ChannelDeleteEvent',
    'ChannelPinsUpdateEvent',
)


class ChannelEvent(str, enum.Enum):
    CREATE = 'CHANNEL_CREATE'
    UPDATE = 'CHANNEL_UPDATE'
    DELETE = 'CHANNEL_DELETE'
    PINS_UPDATE = 'CHANNEL_PINS_UPDATE'


class ChannelListener(BaseWebSocketListener):
    def __init__(self, *, client: WebSocketClient) -> None:
        super().__init__(client=client)
        self.direct_messages = False

    def enable_direct_messages(self) -> None:
        self.direct_messages = True

    def get_event(self, name: str) -> ChannelEvent:
        return ChannelEvent(name)

    def get_intents(self) -> WebSocketIntents:
        intents = WebSocketIntents.GUILDS

        if self.direct_messages:
            intents |= WebSocketIntents.DIRECT_MESSAGES

        return intents

    async def dispatch_channel_create(self, payload: JSONData) -> ChannelCreateEvent:
        channel = await self.client.channels.upsert(payload)
        return ChannelCreateEvent(channel=channel, payload=payload)

    async def dispatch_channel_update(self, payload: JSONData) -> ChannelUpdateEvent:
        channel = await self.client.channels.upsert(payload)
        return ChannelUpdateEvent(channel=channel, payload=payload)

    async def dispatch_channel_delete(self, payload: JSONData) -> ChannelDeleteEvent:
        try:
            channel = self.client.channels.pop(payload['id'])
        except UnknownModelError:
            channel = None

        return ChannelDeleteEvent(channel=channel, payload=payload)

    async def dispatch_channel_pins_update(self, payload: JSONData) -> ChannelPinsUpdateEvent:
        channel = self.client.channels.wrap_id(payload['channel_id'])

        timestamp = payload.get('last_pin_timestamp')
        if timestamp is not None:
            timestamp = datetime.fromisoformat(timestamp)

        return ChannelPinsUpdateEvent(channel=channel, payload=payload, timestamp=timestamp)

    def wait_for_create(
        self, *, timeout: Optional[float] = None, filter: WaiterFilter[ChannelCreateEvent] = None
    ):
        return self.create_waiter(ChannelEvent.CREATE, timeout=timeout, filter=filter)

    def wait_for_update(
        self, *, timeout: Optional[float] = None, filter: WaiterFilter[ChannelUpdateEvent] = None
    ):
        return self.create_waiter(ChannelEvent.UPDATE, timeout=timeout, filter=filter)

    def wait_for_delete(
        self, *, timeout: Optional[float] = None, filter: WaiterFilter[ChannelDeleteEvent] = None
    ):
        return self.create_waiter(ChannelEvent.DELETE, timeout=timeout, filter=filter)

    def wait_for_pins_update(
        self,
        *,
        timeout: Optional[float] = None,
        filter: WaiterFilter[ChannelPinsUpdateEvent] = None
    ):
        return self.create_waiter(ChannelEvent.PINS_UPDATE, timeout=timeout, filter=filter)


class ChannelCreateEvent:
    __slots__ = ('channel', 'payload')

    def __init__(self, *, channel: BaseChannel, payload: JSONData) -> None:
        self.channel = channel
        self.payload = payload

    def __repr__(self) -> str:
        return f'ChannelCreateEvent(channel={self.channel!r})'


class ChannelUpdateEvent:
    __slots__ = ('channel', 'payload')

    def __init__(self, *, channel: BaseChannel, payload: JSONData) -> None:
        self.channel = channel
        self.payload = payload

    def __repr__(self) -> str:
        return f'ChannelUpdateEvent(channel={self.channel!r})'


class ChannelDeleteEvent:
    __slots__ = ('channel', 'payload')

    def __init__(self, *, channel: BaseChannel, payload: JSONData) -> None:
        self.channel = channel
        self.payload = payload

    def __repr__(self):
        return f'ChannelDeleteEvent(channel={self.channel!r})'


class ChannelPinsUpdateEvent:
    __slots__ = ('channel', 'timestamp', 'payload')

    def __init__(self, *, channel: ModelWrapper, timestamp: datetime, payload: JSONData) -> None:
        self.channel = channel
        self.timestamp = timestamp
        self.payload = payload

    def __repr__(self):
        return (
            f'ChannelPinsUpdateEvent(channel={self.channel}, timestamp={self.timestamp!r})'
        )
