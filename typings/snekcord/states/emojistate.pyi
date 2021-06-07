from typing import Any, ClassVar, SupportsInt, Type, Union
from .basestate import BaseState
from ..client import Baseclient
from ..objects.emojiobject import GuildEmoji
from ..objects.guildobject import Guild
from ..utils import Snowflake

_ConvertableToInt = Union[SupportsInt, str]

class GuildEmojiState(BaseState[Snowflake]):
    __guild_emoji_class__: ClassVar[Type[GuildEmoji]]
    guild: Guild

    def __init__(self, *, client: Baseclient, guild: Guild) -> None: ...
    def upsert(self, data: dict[str, Any]) -> GuildEmoji: ...
    async def fetch(self, emoji: _ConvertableToInt) -> GuildEmoji: ...
    async def fetch_all(self) -> list[GuildEmoji]: ...
