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
from ..utils.json import JsonField, JsonObject
from ..utils.snowflake import Snowflake

T = t.TypeVar('T')


class ChannelType(Enum[int]):
    GUILD_TEXT: t.ClassVar[int]
    DM: t.ClassVar[int]
    GUILD_VOICE: t.ClassVar[int]
    GROUP_DM: t.ClassVar[int]
    GUILD_CATEGORY: t.ClassVar[int]
    GUILD_NEWS: t.ClassVar[int]
    GUILD_STORE: t.ClassVar[int]
    GUILD_NEWS_THREAD: t.ClassVar[int]
    GUILD_PUBLIC_THREAD: t.ClassVar[int]
    GUILD_PRIVATE_THREAD: t.ClassVar[int]
    GUILD_STAGE_VOICE: t.ClassVar[int]


class GuildChannel(BaseObject[Snowflake]):
    name: JsonField[str]
    guild_id: JsonField[Snowflake]
    position: JsonField[int]
    nsfw: JsonField[bool]
    parent_id: JsonField[Snowflake]
    type: JsonField[ChannelType]

    state: ChannelState
    permissions: PermissionOverwriteState

    def __init__(self, *, state: ChannelState) -> None: ...

    @property
    def mention(self) -> str: ...

    @property
    def guild(self) -> Guild | None: ...

    @property
    def parent(self) -> CategoryChannel | None: ...

    async def modify(self: T, **kwargs: t.Any) -> T: ...

    async def delete(self) -> None: ...


class FollowedChannel(JsonObject):
    channel_id: JsonField[Snowflake]
    webhook_id: JsonField[Snowflake]

    state: ChannelState

    def __init__(self, *, state: ChannelState) -> None: ...

    @property
    def channel(self) -> TextChannel: ...


class TextChannel(BaseObject[Snowflake]):
    topic: JsonField[str]
    slowmode: JsonField[int]
    last_message_id: JsonField[Snowflake]

    last_pin_timestamp: datetime | None
    messages: MessageState

    @property
    def last_message(self) -> Message | None: ...

    async def follow(self, webhook_channel: SnowflakeConvertible
                     ) -> FollowedChannel: ...

    async def typing(self) -> None: ...

    async def fetch_pins(self) -> set[Message]: ...


class CategoryChannel(GuildChannel):
    @property
    def children(self) -> t.Generator[GuildChannel, None, None]: ...


class VoiceChannel(GuildChannel):
    bitrate: JsonField[int]
    user_limit: JsonField[int]


class DMChannel(BaseObject[Snowflake]):
    last_message_id: JsonField[Snowflake]
    type: JsonField[ChannelType]

    state: ChannelState

    def __init__(self, *, state: ChannelState) -> None: ...

    async def close(self) -> None: ...
