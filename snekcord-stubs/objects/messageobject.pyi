from __future__ import annotations

import typing as t
from datetime import datetime

from .baseobject import BaseObject
from .channelobject import DMChannel, GuildChannel
from .embedobject import Embed
from .guildobject import Guild
from .memberobject import GuildMember
from .userobject import User
from ..enums import MessageType
from ..flags import MessageFlags
from ..states.messagestate import MessageState
from ..utils.json import JsonArray, JsonField
from ..utils.snowflake import Snowflake


class Message(BaseObject[Snowflake]):
    channel_id: t.ClassVar[JsonField[Snowflake]]
    guild_id: t.ClassVar[JsonField[Snowflake]]
    content: t.ClassVar[JsonField[str]]
    edited_at: t.ClassVar[JsonField[datetime]]
    tts: t.ClassVar[JsonField[bool]]
    mention_everyone: t.ClassVar[JsonField[bool]]
    embeds: t.ClassVar[JsonArray[Embed]]
    nonce: t.ClassVar[JsonField[int | str]]
    pinned: t.ClassVar[JsonField[bool]]
    webhook_id: t.ClassVar[JsonField[Snowflake]]
    type: t.ClassVar[JsonField[MessageType]]
    application: None
    flags: t.ClassVar[JsonField[MessageFlags]]

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
