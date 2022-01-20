from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING, Union

from .base_state import (
    BaseCachedClientState,
    BaseClientState,
    BaseSubState,
)
from ..builders import JSONBuilder
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
from ..rest.endpoints import (
    CREATE_GUILD_CHANNEL,
    GET_GUILD_CHANNELS,
    MODIFY_GUILD_CHANNEL_POSITIONS,
)
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined, undefined

if TYPE_CHECKING:
    from ..json import JSONData
    from ..websockets import ShardWebSocket

__all__ = (
    'ChannelUnwrappable',
    'ChannelPosition',
    'ChannelState',
    'GuildChannelState',
)

ChannelUnwrappable = Union[Snowflake, str, int, BaseChannel, ObjectWrapper]


class ChannelPosition:
    __slots__ = ('position', 'lock_permissions', 'parent')

    def __init__(
        self,
        *,
        position: MaybeUndefined[Optional[int]] = undefined,
        lock_permissions: MaybeUndefined[Optional[bool]] = undefined,
        parent: MaybeUndefined[Optional[ChannelUnwrappable]] = undefined,
    ) -> None:
        self.position = position
        self.lock_permissions = lock_permissions
        self.parent = parent


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

        if type is ChannelType.GUILD_NEWS:
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


class GuildChannelState(BaseSubState):
    def __init__(self, *, superstate: BaseClientState, guild: Guild) -> None:
        super().__init__(superstate=superstate)
        self.guild = guild

    async def upsert(self, data):
        data['guild_id'] = Guild.id.deconstruct(self.guild.id)
        return await super().upsert(data)

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

    async def modify_positions(self, channels: dict[ChannelUnwrappable, ChannelPosition]) -> None:
        positions = []

        for key, value in channels.items():
            body = JSONBuilder()

            body.snowflake('id', self.unwrap_id(key))
            body.int('position', value.position, nullable=True)
            body.bool('lock_permissions', value.lock_permissions, nullable=True)

            if value.parent is not undefined:
                body.snowflake('parent', self.unwrap_id(value.parent), nullable=True)

            positions.append(body)

        await self.client.rest.request(
            MODIFY_GUILD_CHANNEL_POSITIONS, guild_id=self.guild.id, json=positions
        )
