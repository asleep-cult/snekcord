from __future__ import annotations

import enum
from datetime import datetime

from .base_listener import (
    BaseWebSocketListener,
    WebSocketIntents,
)
from ...exceptions import UnknownModelError

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
    def __init__(self, *, client):
        super().__init__(client=client)
        self.direct_messages = False

    def enable_direct_messages(self):
        self.direct_messages = True

    def to_event(self, name):
        return ChannelEvent(name)

    def get_intents(self):
        intents = WebSocketIntents.GUILDS

        if self.direct_messages:
            intents |= WebSocketIntents.DIRECT_MESSAGES

        return intents

    def wait_for_create(self, *, timeout=None, filter=None):
        return self.create_waiter(ChannelEvent.CREATE, timeout=timeout, filter=filter)

    def wait_for_update(self, *, timeout=None, filter=None):
        return self.create_waiter(ChannelEvent.UPDATE, timeout=timeout, filter=filter)

    def wait_for_delete(self, *, timeout=None, filter=None):
        return self.create_waiter(ChannelEvent.DELETE, timeout=timeout, filter=filter)

    def wait_for_pins_update(self, *, timeout=None, filter=None):
        return self.create_waiter(ChannelEvent.PINS_UPDATE, timeout=timeout, filter=filter)


class _ChannelUpsertEvent:
    __slots__ = ('channel', 'payload')

    def __init__(self, *, channel, payload):
        self.channel = channel
        self.payload = payload

    @classmethod
    async def execute(cls, client, payload):
        channel = await client.channels.upsert(payload)
        return cls(channel=channel, payload=payload)


@ChannelListener.event(ChannelEvent.CREATE)
class ChannelCreateEvent(_ChannelUpsertEvent):
    __slots__ = ()

    def __repr__(self):
        return f'ChannelCreateEvent(channel={self.channel!r})'


@ChannelListener.event(ChannelEvent.UPDATE)
class ChannelUpdateEvent(_ChannelUpsertEvent):
    __slots__ = ()

    def __repr__(self):
        return f'ChannelUpdateEvent(channel={self.channel!r})'


@ChannelListener.event(ChannelEvent.DELETE)
class ChannelDeleteEvent:
    __slots__ = ('channel', 'payload')

    def __init__(self, *, channel, payload):
        self.channel = channel
        self.payload = payload

    def __repr__(self):
        return f'ChannelDeleteEvent(channel={self.channel!r})'

    @classmethod
    async def execute(cls, client, payload):
        try:
            channel = client.channels.pop(payload['id'])
        except UnknownModelError:
            channel = None

        return cls(channel=channel, payload=payload)


@ChannelListener.event(ChannelEvent.PINS_UPDATE)
class ChannelPinsUpdateEvent:
    __slots__ = ('channel', 'timestamp', 'payload')

    def __init__(self, *, channel, timestamp, payload):
        self.channel = channel
        self.timestamp = timestamp
        self.payload = payload

    def __repr__(self):
        return (
            f'ChannelPinsUpdateEvent(channel={self.channel}, timestamp={self.timestamp!r})'
        )

    @classmethod
    def execute(cls, client, payload):
        try:
            channel = client.channels.get(payload['id'])
        except UnknownModelError:
            channel = None

        timestamp = payload.get('last_pin_timestamp')
        if timestamp is not None:
            timestamp = datetime.fromisoformat(timestamp)

        return cls(channel=channel, payload=payload, timestamp=timestamp)
