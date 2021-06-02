import enum
from typing import Any, Literal

from .baseobject import BaseObject

from ..utils import JsonTemplate, Snowflake


class ChannelType(enum.IntEnum):
    GUILD_TEXT: Literal[0]
    DM: Literal[1]
    GUILD_VOICE: Literal[2]
    GROUP_DM: Literal[3]
    GUILD_CATEGORY: Literal[4]
    GUILD_NEWS: Literal[5]
    GUILD_STORE: Literal[6]
    GUILD_NEWS_THREAD: Literal[10]
    GUILD_PUBLIC_THREAD: Literal[11]
    GUILD_PRIVATE_THREAD: Literal[12]
    GUILD_STAGE_VOICE: Literal[13]

GuildChannelTemplate: JsonTemplate = ...

class GuildChannel(BaseObject[Snowflake]):
    name: str
    guild_id: Snowflake
    _permission_overwrites: dict[str, Any]
    position: int
    nsfw: bool
    parent_id: Snowflake
    type: int

    @property
    def mention(self) -> str:
        ...

    @property
    def guild(self) -> str:
        ...

TextChannelTemplate: JsonTemplate = ...

class TextChannel(GuildChannel):
    topic: str
    slowmode: int
    last_message_id: Snowflake

VoiceChannelTemplate: JsonTemplate = ...

class VoiceChannel(GuildChannel):
    bitrate: int

DMChannelTemplate: JsonTemplate = ...

class DMChannel(BaseObject[Snowflake]):
    async def close(self) -> None: ...
