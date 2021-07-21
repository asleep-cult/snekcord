from .basestate import BaseState, BaseSubState
from .. import rest
from ..clients.client import ClientClasses
from ..objects.emojiobject import BaseEmoji, UnicodeEmoji
from ..resolvers import resolve_data_uri, resolve_emoji
from ..utils import Snowflake

UNICODE_EMOJIS_BY_SURROGATES = {}
UNICODE_EMOJIS_BY_NAME = {}

try:
    import snekcord.emojis as _emojis  # type: ignore

    for category, emojis in _emojis.ALL_CATEGORIES.items():
        for data in emojis:
            emoji = UnicodeEmoji(category=category, data=data)
            emoji._store(UNICODE_EMOJIS_BY_SURROGATES, UNICODE_EMOJIS_BY_NAME)
except ImportError:
    _emojis = None

__all__ = ('EmojiState', 'GuildEmojiState')


class EmojiState(BaseState):
    @classmethod
    def get_unicode(cls, data, default=None):
        if isinstance(data, str):
            emoji = UNICODE_EMOJIS_BY_NAME.get(data.strip(':'))

            if emoji is not None:
                return emoji

            data = data.encode()

        if isinstance(data, bytes):
            emoji = UNICODE_EMOJIS_BY_SURROGATES.get(data)

            if emoji is not None:
                return emoji

            return ClientClasses.PartialUnicodeEmoji(surrogates=data)

        return default

    def upsert(self, data):
        emoji_id = data['id']

        if emoji_id is not None:
            emoji = self.get(Snowflake(emoji_id))

            if emoji is not None:
                emoji.update(data)
            else:
                emoji = ClientClasses.CustomEmoji.unmarshal(data, state=self)
                emoji.cache()
        else:
            emoji = self.client.emojis.get_unicode(data['name'].encode())

        return emoji

    def resolve(self, emoji):
        if isinstance(emoji, BaseEmoji):
            return emoji

        if isinstance(emoji, int):
            return self.get(emoji)

        if isinstance(emoji, str):
            data = resolve_emoji(emoji)

            if data is not None:
                emoji = self.get(data['id'])

                if emoji is not None:
                    return emoji

                return ClientClasses.PartialCustomEmoji(client=self.client, **data)

        return self.get_unicode(emoji)


class GuildEmojiState(BaseSubState):
    def __init__(self, *, superstate, guild):
        super().__init__(superstate=superstate)
        self.guild = guild

    def upsert(self, data):
        data['guild_id'] = self.guild._json_data_['id']
        emoji = self.superstate.upsert(data)

        self.add_key(emoji.id)

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

    async def create(self, *, name, image, roles=None):
        json = {'name': str(name)}

        json['image'] = await resolve_data_uri(image)

        if roles is not None:
            json['roles'] = Snowflake.try_snowflake_many(roles)

        data = await rest.create_guild_emoji.request(
            self.client.rest, {'guild_id': self.guild.id}, json=json
        )

        return self.superstate.upsert(data)

    async def delete(self, emoji):
        emoji_id = Snowflake.try_snowflake(emoji)

        await rest.delete_guild_emoji.request(
            self.client.rest, {'guild_id': self.guild.id, 'emoji_id': emoji_id}
        )
