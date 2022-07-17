from __future__ import annotations

import enum
import typing
from datetime import datetime

import attr

from ..cache import CachedModel
from ..enums import convert_enum
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined
from .base import SnowflakeObject, SnowflakeWrapper

if typing.TYPE_CHECKING:
    from ..states import ChannelMessagesView
    from .guild import GuildIDWrapper
    from .message import MessageIDWrapper

__all__ = (
    'SupportsChannelID',
    'CachedChannel',
    'ChannelType',
    'Channel',
    'GuildChannel',
    'TextChannel',
    'VoiceChannel',
    'CategoryChannel',
    'ChannelIDWrapper',
)

ChannelT = typing.TypeVar('ChannelT', bound='Channel')

SupportsChannelID = typing.Union[Snowflake, str, int, 'Channel']


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


@attr.s(kw_only=True)
class Channel(SnowflakeObject):
    """The base class for all channels exposing only the id and type fields.
    This class is directly used when a channel with an unknown type is encountered."""

    type: typing.Union[ChannelType, int] = attr.ib(hash=False, repr=True)
    """The type of the channel, may be an :class:`int` if the type is unknown."""

    name: str = attr.ib()
    """The name of the channel."""

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
class GuildChannel(Channel):
    """The base class for all channels within a guild."""

    guild: GuildIDWrapper = attr.ib()
    """A wrapper for the guild the channel is in."""

    position: int = attr.ib()
    """The sorting position of the channel."""

    async def delete(self) -> typing.Optional[Channel]:
        return await self.client.channels.delete(self.id)


@attr.s(kw_only=True)
class TextChannel(GuildChannel):
    """Represents a `snekcord.ChannelType.GUILD_TEXT` channel."""

    parent: ChannelIDWrapper = attr.ib()
    """A wrapper for the category the channel is in."""

    nsfw: typing.Optional[bool] = attr.ib()
    """Whether the channel is NSFW."""

    rate_limit_per_user: int = attr.ib()
    """The amount of seconds a user had to wait before sending another message."""

    last_message: MessageIDWrapper = attr.ib()
    """A wrapper for the last message sent in the channel."""

    last_pin_timestamp: typing.Optional[datetime] = attr.ib()
    """The timestamp of when the last message was pinned in the channel."""

    messages: ChannelMessagesView = attr.ib()
    """A frozen view containing every cached message in the channel."""

    async def trigger_typing(self) -> None:
        return await self.client.channels.trigger_typing(self.id)


@attr.s(kw_only=True)
class VoiceChannel(GuildChannel):
    """Represents a `snekcord.ChannelType.GUILD_VOICE` channel."""

    parent: ChannelIDWrapper = attr.ib()
    """A wrapper for the category the channel is in."""

    nsfw: typing.Optional[bool] = attr.ib()
    """Whether the channel is NSFW."""

    bitrate: int = attr.ib()
    """The bitrate of the channel."""

    user_limit: int = attr.ib()
    """The maximum number of users that can be in the voice channel."""

    rtc_region: typing.Optional[str] = attr.ib()
    """The voice region id for the channel or None if automatic."""


class CategoryChannel(GuildChannel):
    """Represents a `snekcord.ChannelType.GUILD_CATEGORY` channel."""

    __slots__ = ()


class ChannelIDWrapper(SnowflakeWrapper[SupportsChannelID, Channel]):
    async def unwrap_as(self, type: typing.Type[ChannelT]) -> ChannelT:
        """Unwrap the channel and enforce a type check on the return value.
        This is useful when you need a specific channel type.

        Raises
        ------
        TypeError
            Raised when the unwrapped channel is not an instance of the provided type.

        Example
        -------
        ```py
        >>> channel = SnowflakeWrapper(834891949781549056, state=client.channels)
        >>> await channel.unwrap_as(snekcord.TextChannel)
        TextChannel(id=834891949781549056, name='github')
        ```
        """
        channel = await self.unwrap()

        if not isinstance(channel, type):
            raise TypeError(f'Expected channel to be a {type.__name__}')

        return channel
