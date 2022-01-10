from __future__ import annotations

import enum

from .base_models import BaseModel
from .. import json
from ..collection import Collection
from ..exceptions import UnknownModelError

__all__ = (
    'ChannelType',
    'BaseChannel',
    'GuildChannel',
    'TextChannel',
    'VoiceChannel',
    'CategoryChannel',
    'StoreChannel',
)


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


class BaseChannel(BaseModel):
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


class TextChannel(GuildChannel):
    __slots__ = ('messages',)

    slowmode = json.JSONField('rate_limit_per_user')
    topic = json.JSONField('topic')

    def __init__(self, *, state):
        super().__init__(state=state)
        self.messages = self.client.create_message_state(channel=self)


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
        except UnknownModelError:
            return children

        for channel in guild.channels:
            if channel.parent.id == self.id:
                children[channel.id] = channel

        return children


class StoreChannel(GuildChannel):
    __slots__ = ()