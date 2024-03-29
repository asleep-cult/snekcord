from __future__ import annotations

import enum
import typing
from datetime import datetime

import attr

from ..builders import MessageUpdateBuilder
from ..cache import CachedModel
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined, undefined
from .base import SnowflakeObject, SnowflakeWrapper

if typing.TYPE_CHECKING:
    from .channel import ChannelIDWrapper
    from .guild import GuildIDWrapper
    from .member import MemberIDWrapper
    from .user import UserIDWrapper

__all__ = (
    'CachedMessage',
    'MessageType',
    'MessageFlags',
    'Message',
    'SupportsMessageID',
    'MessageIDWrapper',
)


class CachedMessage(CachedModel):
    id: Snowflake
    channel_id: Snowflake
    guild_id: MaybeUndefined[Snowflake]
    author_id: MaybeUndefined[Snowflake]
    content: typing.Optional[str]
    timestamp: str
    edited_timestamp: typing.Optional[str]
    tts: bool
    mention_everyone: bool
    # mentions, mention_roles, mention_channels
    # attachments, embeds, reactions
    nonce: MaybeUndefined[typing.Union[int, str]]
    pinned: bool
    webhook_id: MaybeUndefined[str]
    type: int
    # activity, application
    application_id: MaybeUndefined[str]
    # message_reference
    flags: MaybeUndefined[int]
    # referenced_message, interaction, thread
    # components, sticker_items


class MessageType(enum.IntEnum):
    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    GUILD_MEMBER_JOIN = 7
    USER_PREMIUM_SUBSCRIPTION = 8
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_1 = 9
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2 = 10
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3 = 11
    CHANNEL_FOLLOW_ADD = 12
    GUILD_DISCOVERY_DISQUALIFIED = 14
    GUILD_DISCOVERY_REQUALIFIED = 15
    GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING = 16
    GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING = 17
    THREAD_CREATED = 18
    REPLY = 19
    CHAT_INPUT_COMMAND = 20
    THREAD_STARTER_MESSAGE = 21
    GUILD_INVITE_REMINDER = 22
    CONTEXT_MENU_COMMAND = 23


class MessageFlags(enum.IntFlag):
    NONE = 0
    CROSSPOSTED = 1 << 0
    IS_CROSSPOST = 1 << 1
    SUPPREDD_EMBEDS = 1 << 2
    SOURCE_MESSAGE_DELETED = 1 << 3
    URGENT = 1 << 4
    HAS_THREAD = 1 << 5
    EPHEMERAL = 1 << 6
    LOADING = 1 << 7


@attr.s(kw_only=True, slots=True, hash=True)
class Message(SnowflakeObject):
    channel: ChannelIDWrapper = attr.ib(eq=False)
    guild: GuildIDWrapper = attr.ib(eq=False)
    author: UserIDWrapper = attr.ib(eq=False)
    member: MemberIDWrapper = attr.ib(eq=False)
    content: typing.Optional[str] = attr.ib(repr=False, eq=False)
    timestamp: datetime = attr.ib(repr=False, eq=False)
    edited_timestamp: typing.Optional[datetime] = attr.ib(repr=False, eq=False)
    tts: bool = attr.ib(eq=False)
    nonce: typing.Optional[typing.Union[int, str]] = attr.ib(repr=False, eq=False)
    pinned: bool = attr.ib(eq=False)
    # webhook: WebhookIDWrapper = attr.ib()
    type: typing.Union[MessageType, int] = attr.ib(eq=False)
    # application: ApplicationIDWrapper = attr.ib()
    flags: MessageFlags = attr.ib(eq=False)

    async def crosspost(self) -> Message:
        return await self.client.messages.crosspost(self.channel.unwrap_id(), self.id)

    async def pin(self) -> None:
        return await self.client.messages.pin(self.channel.unwrap_id(), self.id)

    async def unpin(self) -> None:
        return await self.client.messages.unpin(self.channel.unwrap_id(), self.id)

    def update(
        self,
        *,
        content: MaybeUndefined[typing.Optional[str]] = undefined,
        flags: MaybeUndefined[typing.Optional[MessageFlags]] = undefined,
    ) -> MessageUpdateBuilder:
        return self.client.messages.update(
            self.channel.unwrap_id(),
            self.id,
            content=content,
            flags=flags,
        )

    async def delete(self) -> typing.Optional[Message]:
        return await self.client.messages.delete(self.channel.unwrap_id(), self.id)


SupportsMessageID = typing.Union[Snowflake, str, int, Message]
MessageIDWrapper = SnowflakeWrapper[SupportsMessageID, Message]
