from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from .base_state import (
    BaseState,
    StateCacheMixin,
)
from ..events import (
    ChannelCreateEvent,
    ChannelDeleteEvent,
    ChannelEvent,
    ChannelPinsUpdateEvent,
    ChannelUpdateEvent,
)
from ..objects import (
    BaseChannel,
    CategoryChannel,
    ChannelType,
    GuildChannel,
    ObjectWrapper,
    StoreChannel,
    TextChannel,
    VoiceChannel,
)
from ..snowflake import Snowflake

if TYPE_CHECKING:
    from ..json import JSONData
    from ..websockets import ShardWebSocket

__all__ = ('ChannelState',)


class ChannelState(BaseState, StateCacheMixin):
    @classmethod
    def unwrap_id(cls, object) -> Snowflake:
        if isinstance(object, Snowflake):
            return object

        if isinstance(object, (str, int)):
            return Snowflake(object)

        if isinstance(object, BaseChannel):
            return object.id

        if isinstance(object, ObjectWrapper):
            if isinstance(object.state, cls):
                return object.id

            raise TypeError('Expected ObjectWrapper created by ChannelState')

        raise TypeError('Expected Snowflake, str, int, BaseChannel or ObjectWrapper')

    def get_type(self, type):
        if type is ChannelType.GUILD_CATEGORY:
            return CategoryChannel

        if type is ChannelType.GUILD_STORE:
            return StoreChannel

        if type is ChannelType.GUILD_TEXT:
            return TextChannel

        if type is ChannelType.GUILD_VOICE:
            return VoiceChannel

        return BaseChannel

    async def upsert(self, data):
        channel = self.get(data['id'])
        if channel is not None:
            channel.update(data)
        else:
            type = self.get_type(ChannelType(data['type']))
            channel = type.unmarshal(data, state=self)

        if isinstance(channel, GuildChannel):
            guild_id = data.get('guild_id')
            if guild_id is not None:
                channel.guild.set_id(guild_id)

        return channel

    def get_events(self) -> type[ChannelEvent]:
        return ChannelEvent

    def on_create(self):
        return self.on(ChannelEvent.CREATE)

    def on_update(self):
        return self.on(ChannelEvent.UPDATE)

    def on_delete(self):
        return self.on(ChannelEvent.DELETE)

    def on_pins_update(self):
        return self.on(ChannelEvent.PINS_UPDATE)

    async def dispatch_create(self, shard: ShardWebSocket, payload: JSONData) -> ChannelCreateEvent:
        channel = await self.upsert(payload)
        return ChannelCreateEvent(shard=shard, payload=payload, channel=channel)

    async def dispatch_update(self, shard: ShardWebSocket, payload: JSONData) -> ChannelUpdateEvent:
        channel = await self.upsert(payload)
        return ChannelUpdateEvent(shard=shard, payload=payload, channel=channel)

    async def dispatch_delete(self, shard: ShardWebSocket, payload: JSONData) -> ChannelDeleteEvent:
        try:
            channel = self.pop(payload['id'])
        except KeyError:
            channel = None

        return ChannelDeleteEvent(shard=shard, payload=payload, channel=channel)

    async def dispatch_pins_update(
        self, shard: ShardWebSocket, payload: JSONData
    ) -> ChannelPinsUpdateEvent:
        channel = self.wrap_id(payload['channel_id'])

        timestamp = payload.get('timestamp')
        if timestamp is not None:
            timestamp = datetime.fromisoformat(timestamp)

        return ChannelPinsUpdateEvent(
            shard=shard, payload=payload, channel=channel, timestmap=timestamp
        )
