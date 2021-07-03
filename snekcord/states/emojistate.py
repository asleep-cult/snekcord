from .basestate import BaseState
from .. import rest
from ..clients.client import ClientClasses
from ..objects.emojiobject import _get_builtin_emoji
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
            emoji = _get_builtin_emoji(data['name'].encode())

        return emoji

    async def fetch(self, emoji):
        emoji_id = Snowflake.try_snowflake(emoji)

        data = await rest.get_guild_emoji.request(
            self.client.rest, {'guild_id': self.guild.id, 'emoji_id': emoji_id}
        )

        return self.upsert(data)

    async def fetch_all(self):
        data = await rest.get_guild_emojis.request(
            self.client.rest, {'guild_id': self.guild.id}
        )

        return [self.upsert(emoji) for emoji in data]

    async def delete(self, emoji):
        emoji_id = Snowflake.try_snowflake(emoji)

        await rest.delete_guild_emoji.request(
            self.client.rest, {'guild_id': self.guild.id, 'emoji_id': emoji_id}
        )
