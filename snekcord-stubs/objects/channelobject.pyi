from __future__ import annotations

import typing as t
from datetime import datetime

from .baseobject import BaseObject
from .guildobject import Guild
from .messageobject import Message
from ..states.channelstate import ChannelState
from ..states.messagestate import MessageState
from ..states.overwritestate import PermissionOverwriteState
from ..typedefs import SnowflakeConvertible
from ..utils.enum import Enum
from ..utils.json import JsonObject, JsonTemplate
from ..utils.snowflake import Snowflake

T = t.TypeVar('T')


class ChannelType(Enum[int]):
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


GuildChannelTemplate: JsonTemplate = ...


class GuildChannel(BaseObject[Snowflake], template=GuildChannelTemplate):
    name: str
    guild_id: Snowflake
    position: int
    nsfw: bool
    parent_id: Snowflake
    type: ChannelType
    permissions: PermissionOverwriteState

    state: ChannelState

    def __init__(self, *, state: ChannelState) -> None: ...

    @property
    def mention(self) -> str: ...

    @property
    def guild(self) -> Guild | None: ...

    @property
    def parent(self) -> CategoryChannel | None: ...

    async def modify(self: T, **kwargs: t.Any) -> T: ...

    async def delete(self) -> None: ...


FollowedChannelTemplate: JsonTemplate = ...


class FollowedChannel(JsonObject, template=FollowedChannelTemplate):
    channel_id: Snowflake
    webhook_id: Snowflake
    state: ChannelState

    def __init__(self, *, state: ChannelState) -> None: ...

    @property
    def channel(self) -> TextChannel: ...


TextChannelTemplate: JsonTemplate = ...


class TextChannel(BaseObject[Snowflake], template=TextChannelTemplate):
    topic: str
    slowmode: int
    last_message_id: Snowflake
    last_pin_timestamp: datetime | None
    messages: MessageState

    @property
    def last_message(self) -> Message | None: ...

    async def follow(self, webhook_channel: SnowflakeConvertible
                     ) -> FollowedChannel: ...

    async def typing(self) -> None: ...

    async def fetch_pins(self) -> set[Message]: ...


class CategoryChannel(GuildChannel, template=GuildChannelTemplate):
    @property
    def children(self) -> t.Generator[GuildChannel, None, None]: ...


VoiceChannelTemplate: JsonTemplate = ...


class VoiceChannel(GuildChannel, template=VoiceChannelTemplate):
    bitrate: int
    user_limit: int


DMChannelTemplate: JsonTemplate = ...


class DMChannel(BaseObject, template=DMChannelTemplate):
    last_message_id: Snowflake
    type: ChannelType

    state: ChannelState

    def __init__(self, *, state: ChannelState) -> None: ...

    async def close(self) -> None: ...
