from . import structures
from .state import BaseState


class GuildEmoji(structures.GuildEmoji):
    __slots__ = (
        '_state', 'guild', 'user'
    )

    def __init__(self, *, state, guild):
        self._state = state
        self.guild = guild
        self.user = None

    @property
    def roles(self):
        return [self.guild.roles.get(r) for r in self._roles]

    def __str__(self):
        if self.id is None:
            return self.name
        elif self.animated:
            return '<a:{0.name}:{0.id}>'.format(self)
        else:
            return '<:{0.name}:{0.id}>'.format(self)

    async def delete(self):
        rest = self._state.client.rest
        await rest.delete_guild_emoji(self.guild.id, self.id)

    async def edit(self, name=None, roles=None):
        rest = self._state.client.rest
        await rest.modify_guild_emoji(self.guild.id, self.id, name, roles)

    def to_dict(self):
        dct = super().to_dict()

        if self.user is not None:
            dct['user'] = self.user.to_dict()

        dct['roles'] = [role.id for role in self.roles]

        return dct

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)

        if self._user is not None:
            self.user = self._state.client.users.append(self._user)


class GuildEmojiState(BaseState):
    def __init__(self, *, client, guild):
        super().__init__(client=client)
        self.guild = guild

    def append(self, data):
        emoji = self.get(data['id'])
        if emoji is not None:
            emoji._update(data)
            return emoji

        emoji = GuildEmoji.unmarshal(data, state=self, guild=self.guild)
        self._items[emoji.id] = emoji
        return emoji

    async def fetch(self, emoji_id):
        rest = self.client.rest
        data = await rest.get_guild_emoji(self.guild.id, emoji_id)
        emoji = self.append(data)
        return emoji

    async def fetch_all(self):
        rest = self.client.rest
        data = await rest.get_guild_emojis(self.guild.id)
        emojis = [self.append(emoji) for emoji in data]
        return emojis

    async def create(self, name, image, roles=None):
        rest = self.client.rest
        data = await rest.create_guild_emoji(self.guild.id, name, image, roles)
        emoji = self.append(data)
        return emoji
