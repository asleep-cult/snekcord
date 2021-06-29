from __future__ import annotations

import typing as t
from datetime import datetime

from .baseobject import BaseObject
from .channelobject import DMChannel, GuildChannel
from .embedobject import Embed
from .guildobject import Guild
from .memberobject import GuildMember
from .userobject import User
from ..states.messagestate import MessageState
from ..utils.bitset import Bitset, Flag
from ..utils.enum import Enum
from ..utils.json import JsonArray, JsonField
from ..utils.snowflake import Snowflake


class MessageType(Enum[int]):
    DEFAULT: t.ClassVar[int]
    RECIPIENT_ADD: t.ClassVar[int]
    RECIPIENT_REMOVE: t.ClassVar[int]
    CALL: t.ClassVar[int]
    CHANNEL_NAME_CHANGE: t.ClassVar[int]
    CHANNEL_ICON_CHANGE: t.ClassVar[int]
    CHANNEL_PINNED_MESSAGE: t.ClassVar[int]
    GUILD_MEMBER_JOIN: t.ClassVar[int]
    USER_PERMIUM_GUILD_SUBSCRIPTION: t.ClassVar[int]
    USER_PERMIUM_GUILD_SUBSCRIPTION_TIER_1: t.ClassVar[int]
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2: t.ClassVar[int]
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3: t.ClassVar[int]
    CHANNEL_FOLLOW_ADD: t.ClassVar[int]
    GUILD_DISCOVERY_DISQUALIFIED: t.ClassVar[int]
    GUILD_DISCOVERY_REQUALIFIED: t.ClassVar[int]
    GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING: t.ClassVar[int]
    GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING: t.ClassVar[int]
    THREAD_CREATED: t.ClassVar[int]
    REPLY: t.ClassVar[int]
    APPLICATION_COMMAND: t.ClassVar[int]
    THREAD_STARTER_MESSAGE: t.ClassVar[int]
    GUILD_INVITE_REMINDER: t.ClassVar[int]


class MessageFlags(Bitset):
    CROSSPOSTED: t.ClassVar[Flag]
    IS_CROSSPOST: t.ClassVar[Flag]
    SUPPRESS_EMBEDS: t.ClassVar[Flag]
    SOURCE_MESSAGE_DELETED: t.ClassVar[Flag]
    URGENT: t.ClassVar[Flag]
    HAS_THREAD: t.ClassVar[Flag]
    EPHEMERAL: t.ClassVar[Flag]
    LOADING: t.ClassVar[Flag]


class Message(BaseObject[Snowflake]):
    channel_id: JsonField[Snowflake]
    guild_id: JsonField[Snowflake]
    content: JsonField[str]
    edited_at: JsonField[datetime]
    tts: JsonField[bool]
    mention_everyone: JsonField[bool]
    embeds: JsonArray[Embed]
    nonce: JsonField[int | str]
    pinned: JsonField[bool]
    webhook_id: JsonField[Snowflake]
    type: JsonField[MessageType]
    application: None
    flags: JsonField[MessageFlags]

    state: MessageState
    author: User | None
    member: GuildMember | None

    def __init__(self, *, state: MessageState) -> None: ...

    @property
    def channel(self) -> DMChannel | GuildChannel: ...

    @property
    def guild(self) -> Guild | None: ...

    async def crosspost(self) -> Message: ...

    async def delete(self) -> None: ...
