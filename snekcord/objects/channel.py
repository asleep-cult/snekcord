from __future__ import annotations

import enum
import typing
from datetime import datetime

import attr

from .base import SnowflakeObject
from ..cache import CachedModel
from ..rest.endpoints import (
    DELETE_CHANNEL,
    TRIGGER_CHANNEL_TYPING,
)
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined

if typing.TYPE_CHECKING:
    from ..states import (
        ChannelMessagesView,
        ChannelIDWrapper,
        GuildIDWrapper,
        MessageIDWrapper,
        SupportsChannelID,
    )
else:
    SupportsChannelID = typing.NewType('SupportsChannelID', typing.Any)

__all__ = (
    'CachedChannel',
    'ChannelType',
    'BaseChannel',
    'GuildChannel',
    'TextChannel',
    'VoiceChannel',
    'CategoryChannel',
    'StoreChannel',
)


class CachedChannel(CachedModel):
    id: Snowflake
    type: int
    guild_id: MaybeUndefined[Snowflake]
    position: MaybeUndefined[int]
    # permission_overwrites: MaybeUndefined[typing.List]
    name: MaybeUndefined[str]
    topic: MaybeUndefined[typing.Optional[str]]
    nsfw: MaybeUndefined[bool]
    last_message_id: MaybeUndefined[typing.Optional[str]]
    bitrate: MaybeUndefined[int]
    user_limit: MaybeUndefined[int]
    rate_limit_per_user: MaybeUndefined[int]
    recipient_ids: MaybeUndefined[typing.List[str]]
    icon: MaybeUndefined[typing.Optional[str]]
    owner_id: MaybeUndefined[str]
    application_id: MaybeUndefined[str]
    parent_id: MaybeUndefined[typing.Optional[str]]
    last_pin_timestamp: MaybeUndefined[typing.Optional[str]]
    rtc_region: MaybeUndefined[typing.Optional[str]]
    video_quality_mode: MaybeUndefined[int]


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
class BaseChannel(SnowflakeObject[SupportsChannelID]):
    type: typing.Union[ChannelType, int] = attr.ib(hash=False, repr=True)

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
    guild: GuildIDWrapper = attr.ib()
    name: str = attr.ib()
    position: int = attr.ib()

    async def delete(self) -> None:
        await self.client.rest.request_api(DELETE_CHANNEL, channel_id=self.id)


@attr.s(kw_only=True)
class TextChannel(GuildChannel):
    parent: ChannelIDWrapper = attr.ib()
    nsfw: typing.Optional[bool] = attr.ib()
    rate_limit_per_user: int = attr.ib()
    last_message: MessageIDWrapper = attr.ib()
    last_pin_timestamp: typing.Optional[datetime] = attr.ib()
    messages: ChannelMessagesView = attr.ib()

    async def trigger_typing(self) -> None:
        await self.client.rest.request_api(TRIGGER_CHANNEL_TYPING, channel_id=self.id)


@attr.s(kw_only=True)
class VoiceChannel(GuildChannel):
    parent: ChannelIDWrapper = attr.ib()
    nsfw: typing.Optional[bool] = attr.ib()
    bitrate: int = attr.ib()
    user_limit: int = attr.ib()
    rtc_region: typing.Optional[str] = attr.ib()


class CategoryChannel(GuildChannel):
    __slots__ = ()


class StoreChannel(GuildChannel):
    __slots__ = ()
