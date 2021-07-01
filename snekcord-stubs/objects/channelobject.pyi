from __future__ import annotations

import typing as t
from datetime import datetime

from .baseobject import BaseObject
from .guildobject import Guild
from .messageobject import Message
from ..enums import ChannelType
from ..states.channelstate import ChannelState
from ..states.messagestate import MessageState
from ..states.overwritestate import PermissionOverwriteState
from ..typedefs import SnowflakeConvertible
from ..utils import JsonField, JsonObject, Snowflake

T = t.TypeVar('T')


class GuildChannel(BaseObject[Snowflake]):
    name: t.ClassVar[JsonField[str]]
    guild_id: t.ClassVar[JsonField[Snowflake]]
    position: t.ClassVar[JsonField[int]]
    nsfw: t.ClassVar[JsonField[bool]]
    parent_id: t.ClassVar[JsonField[Snowflake]]
    type: t.ClassVar[JsonField[ChannelType]]

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
    channel_id: t.ClassVar[JsonField[Snowflake]]
    webhook_id: t.ClassVar[JsonField[Snowflake]]

    state: ChannelState

    def __init__(self, *, state: ChannelState) -> None: ...

    @property
    def channel(self) -> TextChannel: ...


class TextChannel(BaseObject[Snowflake]):
    topic: t.ClassVar[JsonField[str]]
    slowmode: t.ClassVar[JsonField[int]]
    last_message_id: t.ClassVar[JsonField[Snowflake]]

    last_pin_timestamp: datetime | None
    messages: MessageState

    @property
    def last_message(self) -> Message | None: ...

    async def follow(self, webhook_channel: SnowflakeConvertible) -> FollowedChannel: ...

    async def typing(self) -> None: ...

    async def fetch_pins(self) -> list[Message]: ...


class CategoryChannel(GuildChannel):
    @property
    def children(self) -> t.Generator[GuildChannel, None, None]: ...


class VoiceChannel(GuildChannel):
    bitrate: t.ClassVar[JsonField[int]]
    user_limit: t.ClassVar[JsonField[int]]


class DMChannel(BaseObject[Snowflake]):
    last_message_id: t.ClassVar[JsonField[Snowflake]]
    type: t.ClassVar[JsonField[ChannelType]]

    state: ChannelState

    def __init__(self, *, state: ChannelState) -> None: ...

    async def close(self) -> None: ...
