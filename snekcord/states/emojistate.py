from .basestate import BaseState
from .. import rest
from ..clients.client import ClientClasses
from ..objects.emojiobject import BUILTIN_EMOJIS
from ..utils import Snowflake

__all__ = ('GuildEmojiState',)


class GuildEmojiState(BaseState):
    def __init__(self, *, client, guild):
        super().__init__(client=client)
        self.guild = guild

    def upsert(self, data):
        emoji_id = data['id']
        if emoji_id is not None:
            emoji = self.get(Snowflake(emoji_id))
            if emoji is not None:
                emoji.update(data)
            else:
                emoji = ClientClasses.GuildEmoji.unmarshal(data, state=self)
                emoji.cache()
        else:
            surrogates = data['name'].encode()
            emoji = BUILTIN_EMOJIS.get(surrogates)

        return emoji

    async def fetch(self, emoji):
        emoji_id = Snowflake.try_snowflake(emoji)

        data = await rest.get_guild_emoji.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id, emoji_id=emoji_id))

        return self.upsert(data)

    async def fetch_all(self):
        data = await rest.get_guild_emojis.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id))

        return [self.upsert(emoji) for emoji in data]
