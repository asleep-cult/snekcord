from __future__ import annotations

import enum
import typing
from datetime import datetime

import attr

from ..cache import CachedModel
from ..objects import SnowflakeObject
from ..undefined import MaybeUndefined

if typing.TYPE_CHECKING:
    from ..states import (
        ApplicationIDWrapper,
        ChannelIDWrapper,
        GuildIDWrapper,
        MessageState,
        UserIDWrapper,
        SupportsMessageID,
        WebhookIDWrapper,
    )
else:
    SupportsMessageID = typing.NewType('SupportsChannelID', typing.Any)

__all__ = (
    'CachedMessage',
    'MessageType',
    'MessageFlags',
    'Message',
)


class CachedMessage(CachedModel):
    id: str
    channel_id: str
    guild_id: MaybeUndefined[str]
    author_id: MaybeUndefined[str]
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


@attr.s(kw_only=True)
class Message(SnowflakeObject[SupportsMessageID]):
    state: MessageState

    channel: ChannelIDWrapper = attr.ib()
    guild: GuildIDWrapper = attr.ib()
    author: UserIDWrapper = attr.ib()
    content: typing.Optional[str] = attr.ib()
    timestamp: datetime = attr.ib()
    edited_timestamp: typing.Optional[datetime] = attr.ib()
    tts: bool = attr.ib()
    nonce: typing.Optional[typing.Union[int, str]] = attr.ib()
    pinned: bool = attr.ib()
    webhook: WebhookIDWrapper = attr.ib()
    type: typing.Union[MessageType, int] = attr.ib()
    application: ApplicationIDWrapper = attr.ib()
    flags: MessageFlags = attr.ib()
