from __future__ import annotations

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
from ..utils.json import JsonTemplate
from ..utils.snowflake import Snowflake


class MessageType(Enum[int]):
    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    GUILD_MEMBER_JOIN = 7
    USER_PERMIUM_GUILD_SUBSCRIPTION = 8
    USER_PERMIUM_GUILD_SUBSCRIPTION_TIER_1 = 9
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2 = 10
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3 = 11
    CHANNEL_FOLLOW_ADD = 12
    GUILD_DISCOVERY_DISQUALIFIED = 14
    GUILD_DISCOVERY_REQUALIFIED = 15
    GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING = 16
    GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING = 17
    THREAD_CREATED = 18
    REPLY = 19
    APPLICATION_COMMAND = 20
    THREAD_STARTER_MESSAGE = 21
    GUILD_INVITE_REMINDER = 22


class MessageFlags(Bitset):
    CROSSPOSTED = Flag(0)
    IS_CROSSPOST = Flag(1)
    SUPPRESS_EMBEDS = Flag(2)
    SOURCE_MESSAGE_DELETED = Flag(3)
    URGENT = Flag(4)
    HAS_THREAD = Flag(5)
    EPHEMERAL = Flag(7)
    LOADING = Flag(8)


MessageTemplate: JsonTemplate = ...


class Message(BaseObject[Snowflake]):
    channel_id: Snowflake
    guild_id: Snowflake
    content: str
    edited_at: datetime
    tts: bool
    mention_everyone: bool
    embeds: list[Embed]
    nonce: int | str
    pinned: bool
    webhook_id: Snowflake
    type: MessageType
    application: None
    flags: MessageFlags

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
