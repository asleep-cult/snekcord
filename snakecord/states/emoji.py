from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseState, SnowflakeMapping, WeakValueSnowflakeMapping
from ..objects.emoji import GuildEmoji

if TYPE_CHECKING:
    from ..manager import BaseManager
    from ..objects.guild import Guild


class GuildEmojiState(BaseState):
    __container__ = SnowflakeMapping
    __recycled_container__ = WeakValueSnowflakeMapping
    __guild_emoji_class__ = GuildEmoji

    def __init__(self, *, manager: BaseManager, guild: Guild):
        super().__init__(manager=manager)
        self.guild = guild

    @classmethod
    def set_guild_emoji_class(cls, klass: type):
        cls.__guild_emoji_class__ = klass

    def append(self, data: dict, *args, **kwargs):
        emoji = self.get(data['id'])
        if emoji is not None:
            emoji._update(data)
        else:
            emoji = self.__guild_emoji_class__.unmarshal(
                data, state=self, guild=self.guild, *args, **kwargs)
            emoji.cache()

        return emoji
