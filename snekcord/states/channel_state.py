from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional, TYPE_CHECKING, Union

from .base_state import (
    CachedEventState,
    CachedStateView,
    OnDecoratorT,
)
from ..builders import JSONBuilder
from ..events import (
    BaseEvent,
    ChannelCreateEvent,
    ChannelDeleteEvent,
    ChannelEvents,
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
from ..rest.endpoints import (
    CREATE_GUILD_CHANNEL,
    GET_GUILD_CHANNELS,
    MODIFY_GUILD_CHANNEL_POSITIONS,
)
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined, undefined

if TYPE_CHECKING:
    from ..json import JSONData
    from ..websockets import Shard

__all__ = (
    'ChannelUnwrappable',
    'ChannelPosition',
    'ChannelState',
    'GuildChannelState',
)

SupportsChannel = Union[Snowflake, str, int, BaseChannel, ObjectWrapper]


class ChannelState(CachedEventState):
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

        if type is ChannelType.GUILD_NEWS:
            return TextChannel

        if type is ChannelType.GUILD_VOICE:
            return VoiceChannel

        return BaseChannel

    async def upsert(self, data):
        """
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
        """

    def on_create(self) -> OnDecoratorT[ChannelCreateEvent]:
        return self.on(ChannelEvents.CREATE)

    def on_update(self) -> OnDecoratorT[ChannelUpdateEvent]:
        return self.on(ChannelEvents.UPDATE)

    def on_delete(self) -> OnDecoratorT[ChannelDeleteEvent]:
        return self.on(ChannelEvents.DELETE)

    def on_pins_update(self) -> OnDecoratorT[ChannelPinsUpdateEvent]:
        return self.on(ChannelEvents.PINS_UPDATE)

    def get_events(self) -> Iterable[str]:
        return ChannelEvents

    def get_intents(self) -> WebSocketIntents:
        return WebSocketIntents.GUILDS

    async def process(self, event: str, shard: Shard, payload: JSONData) -> BaseEvent:
        event = ChannelEvents(event)

        if event is ChannelEvents.CREATE:
            channel = await self.upsert(payload)
            return ChannelCreateEvent(shard=shard, payload=payload, channel=channel)

        if event is ChannelEvents.UPDATE:
            channel = await self.upsert(payload)
            return ChannelUpdateEvent(shard=shard, payload=payload, channel=channel)

        if event is ChannelEvents.DELETE:
            channel = self.pop(payload['id'])
            return ChannelDeleteEvent(shard=shard, payload=payload, channel=channel)

        if event is ChannelEvents.PINS_UPDATE:
            channel = self.wrap_id(payload['channel_id'])

            timestamp = payload.get('timestamp')
            if timestamp is not None:
                timestamp = datetime.fromisoformat(timestamp)

            return ChannelPinsUpdateEvent(
                shard=shard, payload=payload, channel=channel, timestmap=timestamp
            )


class GuildChannelState(CachedStateView):
    def __init__(self, *, state: ChannelState, guild: Guild) -> None:
        super().__init__(state=state)
        self.guilds = guild

    async def fetch_all(self) -> list[BaseChannel]:
        channels = await self.client.rest.request(GET_GUILD_CHANNELS, guild_id=self.guild.id)
        assert isinstance(channels, list)

        return [await self.upsert(channel) for channel in channels]

    async def create(
        self,
        *,
        name: str,
        type: MaybeUndefined[ChannelType] = undefined,
        topic: MaybeUndefined[str] = undefined,
        bitrate: MaybeUndefined[int] = undefined,
        user_limit: MaybeUndefined[int] = undefined,
        slowmode: MaybeUndefined[int] = undefined,
        position: MaybeUndefined[int] = undefined,
        permissions=undefined,
        parent: MaybeUndefined[ChannelUnwrappable] = undefined,
        nsfw: MaybeUndefined[bool] = undefined,
    ) -> BaseChannel:
        body = JSONBuilder()

        body.str('name', name)
        body.int('type', type)
        body.str('topic', topic)
        body.int('bitrate', bitrate)
        body.int('user_limit', user_limit)
        body.int('rate_limit_per_user', slowmode)
        body.int('position', position)

        if parent is not undefined:
            body.snowflake('parent', self.unwrap_id(parent))

        body.bool('nsfw', nsfw)

        channel = await self.client.rest.request(
            CREATE_GUILD_CHANNEL, guild_id=self.guild.id, json=body
        )
        assert isinstance(channel, dict)

        return await self.upsert(channel)

    """
    async def modify_positions(self, channels: dict[ChannelUnwrappable, ChannelPosition]) -> None:
        positions = []

        for channel, position in channels.items():
            body = JSONBuilder()

            body.snowflake('id', self.unwrap_id(channel))
            body.int('position', position.position, nullable=True)
            body.bool('lock_permissions', position.lock_permissions, nullable=True)

            if position.parent is not undefined:
                body.snowflake('parent', self.unwrap_id(position.parent), nullable=True)

            positions.append(body)

        await self.client.rest.request(
            MODIFY_GUILD_CHANNEL_POSITIONS, guild_id=self.guild.id, json=positions
        )
    """
