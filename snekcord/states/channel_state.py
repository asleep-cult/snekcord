from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Union

from .base_state import (
    CachedEventState,
    OnDecoratorT,
)
from ..events import (
    ChannelCreateEvent,
    ChannelDeleteEvent,
    ChannelEvents,
    ChannelPinsUpdateEvent,
    ChannelUpdateEvent,
)
from ..objects import (
    BaseChannel,
    CachedChannel,
    CategoryChannel,
    ChannelType,
    TextChannel,
    VoiceChannel,
)
from ..snowflake import Snowflake

if TYPE_CHECKING:
    from ..json import JSONData
    from ..websockets import Shard

SupportsChannel = Union[Snowflake, str, int, BaseChannel]


class ChannelState(CachedEventState[SupportsChannel, Snowflake, CachedChannel, BaseChannel]):
    def to_unique(self, object: SupportsChannel) -> Snowflake:
        if isinstance(object, Snowflake):
            return object

        if isinstance(object, (str, int)):
            return Snowflake(object)

        if isinstance(object, BaseChannel):
            return object.id

        raise TypeError('Expected Snowflake, str, int or BaseChannel')

    async def upsert(self, data) -> BaseChannel:
        channel = await self.cache.get(data['id'])
        if channel is None:
            channel = CachedChannel.unmarshal(data)
        else:
            channel.update(data)

        await channel.commit()
        return self.from_cached(channel)

    def from_cached(self, cached: CachedChannel) -> BaseChannel:
        try:
            type = ChannelType(cached.type)
        except TypeError:
            type = int(cached.type)

        if type is ChannelType.GUILD_CATEGORY:
            return CategoryChannel(
                state=self,
                id=Snowflake(cached.id),
                type=type,
                guild_id=Snowflake(cached.guild_id),
                parent_id=Snowflake(cached.parent_id),
                name=cached.name,
                position=cached.position,
                nsfw=cached.nsfw,
            )

        if type is ChannelType.GUILD_TEXT:
            return TextChannel(
                state=self,
                id=Snowflake(cached.id),
                type=type,
                guild_id=Snowflake(cached.guild_id),
                parent_id=Snowflake(cached.parent_id),
                name=cached.name,
                position=cached.position,
                nsfw=cached.nsfw,
                rate_limit_per_user=cached.rate_limit_per_user,
                last_message_id=Snowflake(cached.last_message_id),
                default_auto_archive_duration=cached.default_auto_archive_duration,
                last_pin_timestamp=datetime.fromisoformat(cached.last_pin_timestamp),
            )

        if type is ChannelType.GUILD_VOICE:
            return VoiceChannel(
                state=self,
                id=Snowflake(cached.id),
                type=type,
                guild_id=Snowflake(cached.guild_id),
                parent_id=Snowflake(cached.parent_id),
                name=cached.name,
                position=cached.position,
                nsfw=cached.nsfw,
                bitrate=cached.bitrate,
                user_limit=cached.user_limit,
                rtc_origin=cached.rtc_origin,
            )

        return BaseChannel(state=self, id=Snowflake(cached.id), type=type)

    def on_create(self) -> OnDecoratorT[ChannelCreateEvent]:
        return self.on(ChannelEvents.CREATE)

    def on_update(self) -> OnDecoratorT[ChannelUpdateEvent]:
        return self.on(ChannelEvents.UPDATE)

    def on_delete(self) -> OnDecoratorT[ChannelDeleteEvent]:
        return self.on(ChannelEvents.DELETE)

    def on_pins_update(self) -> OnDecoratorT[ChannelPinsUpdateEvent]:
        return self.on(ChannelEvents.PINS_UPDATE)

    async def process(self, event: str, shard: Shard, payload: JSONData) -> None:
        event = ChannelEvents(event)

        if event is ChannelEvents.CREATE:
            channel = await self.upsert(payload)
            return ChannelCreateEvent(shard=shard, payload=payload, channel=channel)

        if event is ChannelEvents.UPDATE:
            channel = await self.upsert(payload)
            return ChannelUpdateEvent(shard=shard, payload=payload, channel=channel)

        if event is ChannelEvents.DELETE:
            channel = await self.delete(payload['id'])
            return ChannelDeleteEvent(shard=shard, payload=payload, channel=channel)

        if event is ChannelEvents.PINS_UPDATE:
            channel = await self.get(payload['channel_id'])

            timestamp = payload.get('timestamp')
            if timestamp is not None:
                timestamp = datetime.fromisoformat(timestamp)

            return ChannelPinsUpdateEvent(
                shard=shard, payload=payload, channel=channel, timestamp=timestamp
            )
