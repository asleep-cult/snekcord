from __future__ import annotations

import enum
import typing
from datetime import datetime

import attr

from ..cache import CachedModel
from ..enums import convert_enum
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined
from .base import SnowflakeObject

if typing.TYPE_CHECKING:
    from ..states import (
        ChannelIDWrapper,
        ChannelMessagesView,
        GuildIDWrapper,
        MessageIDWrapper,
    )

__all__ = (
    'CachedChannel',
    'ChannelType',
    'BaseChannel',
    'GuildChannel',
    'TextChannel',
    'VoiceChannel',
    'CategoryChannel',
)


class CachedChannel(CachedModel):
    """Represents a raw channel within the channel cache."""

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
    """Represents the different channel types provided by Discord's API."""

    GUILD_TEXT = 0
    """A text channel within a guild."""

    DM = 1
    """A direct message between two users."""

    GUILD_VOICE = 2
    """A voice channel within a guild."""

    GROUP_DM = 3
    """A direct message between multiple users."""

    GUILD_CATEGORY = 4
    """An organizational category within a guild."""

    GUILD_NEWS = 5
    """A channel that users can follow and crosspost into their own guild."""

    GUILD_NEWS_THREAD = 10
    """A temporary sub-channel within a GUILD_NEWS channel."""

    GUILD_PUBLIC_THREAD = 11
    """A temporary sub-channel within a GUILD_TEXT channel."""

    GUILD_PRIVATE_THREAD = 12
    """A temporary sub-channel within a GUILD_TEXT channel that is only
    viewable by those invited and those with the MANAGE_THREADS permission."""

    GUILD_STAGE_VOICE = 13
    """A voice channel for hosting events with an audience."""

    GUILD_DIRECTORY = 14
    """The channel in a hub containing the listed servers."""

    GUILD_FORUM = 15
    """A channel containing only threads."""


@attr.s(kw_only=True)
class BaseChannel(SnowflakeObject):
    """The base class for all channels exposing only the id and type fields.
    This class is directly used when a channel with an unknown type is encountered."""

    type: typing.Union[ChannelType, int] = attr.ib(hash=False, repr=True)

    def is_text(self) -> bool:
        """Returns True if the channel's type is GUILD_TEXT."""
        return self.type is ChannelType.GUILD_TEXT

    def is_news(self) -> bool:
        """Returns True if the channel's type is GUILD_NEWS."""
        return self.type is ChannelType.GUILD_NEWS

    def is_voice(self) -> bool:
        """Returns True if the channel's type is GUILD_VOICE."""
        return self.type is ChannelType.GUILD_VOICE

    def is_stage(self) -> bool:
        """Returns True if the channel's type is GUILD_STAGE_VOICE."""
        return self.type is ChannelType.GUILD_STAGE_VOICE

    def is_category(self) -> bool:
        """Returns True if the channel's type is GUILD_CATEGORY."""
        return self.type is ChannelType.GUILD_CATEGORY

    def is_dm(self) -> bool:
        """Returns True if the channel's type is DM."""
        return self.type is ChannelType.DM

    def is_group_dm(self) -> bool:
        """Returns True if the channel's type is GROUP_DM."""
        return self.type is ChannelType.GROUP_DM

    def is_unknown(self) -> bool:
        """Returns True if the channel's type is unknown."""
        return not isinstance(convert_enum(ChannelType, self.type), ChannelType)


@attr.s(kw_only=True)
class GuildChannel(BaseChannel):
    """The base class for all channels within a guild."""

    guild: GuildIDWrapper = attr.ib()
    name: str = attr.ib()
    position: int = attr.ib()

    async def delete(self) -> typing.Optional[BaseChannel]:
        """Deletes the channel. Requires the MANAGE_CHANNELS permission to execute."""
        return await self.client.channels.delete(self.id)


@attr.s(kw_only=True)
class TextChannel(GuildChannel):
    """Represents a GUILD_TEXT channel."""

    parent: ChannelIDWrapper = attr.ib()
    nsfw: typing.Optional[bool] = attr.ib()
    rate_limit_per_user: int = attr.ib()
    last_message: MessageIDWrapper = attr.ib()
    last_pin_timestamp: typing.Optional[datetime] = attr.ib()
    messages: ChannelMessagesView = attr.ib()

    async def trigger_typing(self) -> None:
        """Triggers the client's typing indicator in this channel."""
        return await self.client.channels.trigger_typing(self.id)


@attr.s(kw_only=True)
class VoiceChannel(GuildChannel):
    """Represents a GUILD_VOICE channel."""

    parent: ChannelIDWrapper = attr.ib()
    nsfw: typing.Optional[bool] = attr.ib()
    bitrate: int = attr.ib()
    user_limit: int = attr.ib()
    rtc_region: typing.Optional[str] = attr.ib()


class CategoryChannel(GuildChannel):
    __slots__ = ()
