from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from .base_state import (
    BaseCachedClientState,
    BaseClientState,
    BaseSubsidiaryState,
)
from ..events import (
    BaseEvent,
    ChannelCreateEvent,
    ChannelDeleteEvent,
    ChannelEvent,
    ChannelPinsUpdateEvent,
    ChannelUpdateEvent,
)
from ..intents import WebSocketIntents
from ..objects import (
    BaseChannel,
    CategoryChannel,
    ChannelType,
    Guild,
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

__all__ = ('ChannelState', 'GuildChannelState')


class ChannelState(BaseCachedClientState):
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

            channel.parent.set_id(data.get('parent_id'))

        return channel

    def on_create(self):
        return self.on(ChannelEvent.CREATE)

    def on_update(self):
        return self.on(ChannelEvent.UPDATE)

    def on_delete(self):
        return self.on(ChannelEvent.DELETE)

    def on_pins_update(self):
        return self.on(ChannelEvent.PINS_UPDATE)

    def get_events(self) -> type[ChannelEvent]:
        return ChannelEvent

    def get_intents(self) -> WebSocketIntents:
        return WebSocketIntents.GUILDS

    async def process_event(
        self, event: str, shard: ShardWebSocket, payload: JSONData
    ) -> BaseEvent:
        event = self.cast_event(event)

        if event is ChannelEvent.CREATE:
            channel = await self.upsert(payload)
            return ChannelCreateEvent(shard=shard, payload=payload, channel=channel)

        if event is ChannelEvent.UPDATE:
            channel = await self.upsert(payload)
            return ChannelUpdateEvent(shard=shard, payload=payload, channel=channel)

        if event is ChannelEvent.DELETE:
            channel = self.pop(payload['id'])
            return ChannelDeleteEvent(shard=shard, payload=payload, channel=channel)

        if event is ChannelEvent.PINS_UPDATE:
            channel = self.wrap_id(payload['channel_id'])

            timestamp = payload.get('timestamp')
            if timestamp is not None:
                timestamp = datetime.fromisoformat(timestamp)

            return ChannelPinsUpdateEvent(
                shard=shard, payload=payload, channel=channel, timestmap=timestamp
            )


class GuildChannelState(BaseSubsidiaryState):
    def __init__(self, *, superstate: BaseClientState, guild: Guild) -> None:
        super().__init__(superstate=superstate)
        self.guild = guild

    async def upsert(self, data):
        data['guild_id'] = Guild.id.deconstruct(self.guild.id)
        return await super().upsert(data)
