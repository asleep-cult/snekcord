from .basestate import BaseState, SnowflakeMapping, WeakValueSnowflakeMapping
from .. import rest
from ..objects.emojiobject import GuildEmoji
from ..utils import Snowflake

__all__ = ('GuildEmojiState',)


class GuildEmojiState(BaseState):
    __container__ = SnowflakeMapping
    __recycled_container__ = WeakValueSnowflakeMapping
    __guild_emoji_class__ = GuildEmoji

    def __init__(self, *, manager, guild):
        super().__init__(manager=manager)
        self.guild = guild

    def append(self, data):
        emoji = self.get(data['id'])
        if emoji is not None:
            emoji.update(data)
        else:
            emoji = self.__guild_emoji_class__.unmarshal(
                data, state=self, guild=self.guild)
            emoji.cache()

        return emoji

    async def fetch(self, emoji):
        emoji_id = Snowflake.try_snowflake(emoji)

        data = await rest.get_guild_emoji.request(
            session=self.manager.rest,
            fmt=dict(guild_id=self.guild.id, emoji_id=emoji_id))

        return self.append(data)

    async def fetch_all(self):
        data = await rest.get_guild_emojis.request(
            session=self.manager.rest,
            fmt=dict(guild_id=self.guild.id))

        return self.extend(data)
