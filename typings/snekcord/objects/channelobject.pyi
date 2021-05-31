import enum
from typing import Literal

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
    @property
    def mention(self) -> str:
        ...

    @property
    def guild(self) -> str:
        ...