from typing import Optional
from .baseobject import BaseObject
from .guildobject import Guild
from .userobject import User
from ..states.emojistate import GuildEmojiState
from ..utils import JsonTemplate, Snowflake

_Emoji = tuple[bytes, tuple[str], float, '_Emoji']

ALL_CATEGORIES: dict[str, _Emoji]

GuildEmojiTemplate: JsonTemplate = ...

class GuildEmoji(BaseObject[Snowflake]):
    guild: Guild
    user: Optional[User]

    def __init__(self, *, state: GuildEmojiState, guild: Guild) -> None: ...
    @property
    def roles(self) -> list[BaseObject[Snowflake]]: ...
