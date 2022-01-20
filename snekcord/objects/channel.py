from __future__ import annotations

import enum
from collections import namedtuple
from typing import TYPE_CHECKING

from .base import SnowflakeObject
from .. import json
from ..builders import JSONBuilder
from ..collection import Collection
from ..exceptions import UnknownObjectError
from ..rest.endpoints import (
    ADD_CHANNEL_PIN,
    CREATE_CHANNEL_FOLLOWER,
    DELETE_CHANNEL,
    GET_CHANNEL_PINS,
    REMOVE_CHANNEL_PIN,
    TRIGGER_CHANNEL_TYPING,
)

if TYPE_CHECKING:
    from .message import Message
    from ..states import ChannelUnwrappable, MessageUnwrappable

__all__ = (
    'ChannelType',
    'BaseChannel',
    'GuildChannel',
    'TextChannel',
    'VoiceChannel',
    'CategoryChannel',
    'StoreChannel',
)

FollowedChannel = namedtuple('FollowedChannel', ('channel', 'webhook'))


class ChannelType(enum.IntEnum):
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6
    GUILD_NEWS_THREAD = 10
    GUILD_PUBLIC_THREAD = 11
    GUILD_PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13


class BaseChannel(SnowflakeObject):
    __slots__ = ()

    type = json.JSONField('type', ChannelType)

    def is_text(self) -> bool:
        return self.type is ChannelType.GUILD_TEXT

    def is_news(self) -> bool:
        return self.type is ChannelType.GUILD_NEWS

    def is_voice(self) -> bool:
        return self.type is ChannelType.GUILD_VOICE

    def is_stage(self) -> bool:
        return self.type is ChannelType.GUILD_STAGE_VOICE

    def is_category(self) -> bool:
        return self.type is ChannelType.GUILD_CATEGORY

    def is_store(self) -> bool:
        return self.type is ChannelType.GUILD_STORE

    def is_dm(self) -> bool:
        return self.type is ChannelType.DM

    def is_group_dm(self) -> bool:
        return self.type is ChannelType.GROUP_DM


class GuildChannel(BaseChannel):
    __slots__ = ('guild', 'parent', 'permissions')

    name = json.JSONField('name')
    position = json.JSONField('position')
    nsfw = json.JSONField('nsfw')

    def __init__(self, *, state):
        super().__init__(state=state)
        self.guild = self.client.guilds.wrap_id(None)
        self.parent = self.client.channels.wrap_id(None)

    async def delete(self) -> None:
        await self.client.rest.request(DELETE_CHANNEL, channel_id=self.id)


class TextChannel(GuildChannel):
    __slots__ = ('messages',)

    slowmode = json.JSONField('rate_limit_per_user')
    topic = json.JSONField('topic')

    def __init__(self, *, state):
        super().__init__(state=state)
        self.messages = self.client.create_message_state(channel=self)

    async def add_follower(self, channel: ChannelUnwrappable) -> FollowedChannel:
        params = JSONBuilder()
        params.snowflake('webhook_channel_id', self.state.unwrap_id(channel))

        followed_channel = await self.client.rest.request(
            CREATE_CHANNEL_FOLLOWER, channel_id=self.channel.id, params=params
        )
        assert isinstance(followed_channel, dict)

        return FollowedChannel(
            self.client.channels.wrap_id(followed_channel['channel_id']),
            self.client.webhooks.wrap_id(followed_channel['webhook_id']),
        )

    async def trigger_typing(self) -> None:
        await self.client.rest.request(TRIGGER_CHANNEL_TYPING, channel_id=self.id)

    async def fetch_pins(self) -> list[Message]:
        data = await self.client.rest.request(GET_CHANNEL_PINS, channel_id=self.id)
        assert isinstance(data, list)

        return [await self.messages.upsert(message) for message in data]

    async def add_pin(self, message: MessageUnwrappable) -> None:
        message_id = self.client.messages.unwrap_id(message)

        await self.client.rest.request(ADD_CHANNEL_PIN, channel_id=self.id, message_id=message_id)

    async def remove_pin(self, message: MessageUnwrappable) -> None:
        message_id = self.client.messages.unwrap_id(message)

        await self.client.rest.request(
            REMOVE_CHANNEL_PIN, channel_id=self.id, message_id=message_id
        )


class VoiceChannel(BaseChannel):
    __slots__ = ()

    bitrate = json.JSONField('bitrate')
    user_limit = json.JSONField('user_limit')
    rtc_region = json.JSONField('rtc_region')


class CategoryChannel(GuildChannel):
    __slots__ = ()

    def get_children(self):
        children = Collection()

        try:
            guild = self.guild.unwrap()
        except UnknownObjectError:
            return children

        for channel in guild.channels:
            if channel.parent.id == self.id:
                children[channel.id] = channel

        return children


class StoreChannel(GuildChannel):
    __slots__ = ()
