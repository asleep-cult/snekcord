from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional, TYPE_CHECKING

import attr

from .base import (
    SerializedObject,
    SnowflakeObject,
)
from .. import json
from ..rest.endpoints import (
    DELETE_CHANNEL,
    TRIGGER_CHANNEL_TYPING,
)
from ..snowflake import Snowflake

if TYPE_CHECKING:
    from ..states import ChannelMessageState

__all__ = (
    'SerializedChannel',
    'ChannelType',
    'BaseChannel',
    'GuildChannel',
    'TextChannel',
    'VoiceChannel',
    'CategoryChannel',
    'StoreChannel',
)


class SerializedChannel(SerializedObject):
    id = json.JSONField('id')
    type = json.JSONField('type')
    guild_id = json.JSONField('guild_id')
    position = json.JSONField('position')
    permission_overwrites = json.JSONField('permission_overwrites')
    name = json.JSONField('name')
    topic = json.JSONField('topic')
    nsfw = json.JSONField('nsfw')
    last_message_id = json.JSONField('last_message_id')
    bitrate = json.JSONField('bitrate')
    user_limit = json.JSONField('user_limit')
    rate_limit_per_user = json.JSONField('rate_limit_per_user')
    recipient_ids = json.JSONArray('recipient_ids')
    icon = json.JSONField('icon')
    owner_id = json.JSONField('owner_id')
    application_id = json.JSONField('application_id')
    parent_id = json.JSONField('parent_id')
    last_pin_timestamp = json.JSONField('last_pin_timestamp')
    rtc_origin = json.JSONField('rtc_origin')
    viedo_quality_mode = json.JSONField('video_quality_mode')
    message_count = json.JSONField('message_count')
    member_count = json.JSONField('member_count')
    thread_metadata = json.JSONField('thread_metadate')
    member = json.JSONField('member')
    default_auto_archive_duration = json.JSONField('default_auto_archive_duration')


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


@attr.s(kw_only=True)
class BaseChannel(SnowflakeObject):
    """The base class for all channels."""

    type: ChannelType = attr.ib(hash=False, repr=True)

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


@attr.s(kw_only=True)
class GuildChannel(BaseChannel):
    """The base class for all guild channels."""

    guild_id: Snowflake = attr.ib()
    parent_id: Snowflake = attr.ib()
    name: str = attr.ib()
    position: int = attr.ib()
    nsfw: bool = attr.ib()

    async def delete(self) -> None:
        await self.client.rest.request(DELETE_CHANNEL, channel_id=self.id)


@attr.s(kw_only=True)
class TextChannel(GuildChannel):
    rate_limit_per_user: int = attr.ib()
    last_message_id: Snowflake = attr.ib()
    default_auto_archive_duration: int = attr.ib()
    last_pin_timestamp: Optional[datetime] = attr.ib()
    messages: ChannelMessageState = attr.ib()

    def __attr_post_init__(self) -> None:
        self.messages = self.client.create_message_state(channel=self)

    async def trigger_typing(self) -> None:
        await self.client.rest.request(TRIGGER_CHANNEL_TYPING, channel_id=self.id)


@attr.s(kw_only=True)
class VoiceChannel(GuildChannel):
    bitrate: int = attr.ib()
    user_limit: int = attr.ib()
    rtc_origin: str = attr.ib()


class CategoryChannel(GuildChannel):
    __slots__ = ()


class StoreChannel(GuildChannel):
    __slots__ = ()
