from . import structures
from .bases import BaseState


class GuildEmoji(structures.GuildEmoji):
    def __init__(self, state, guild):
        self._state = state
        self.guild = guild
        self.roles = []

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
        roles_seen = set()

        for role in self._roles:
            role = self.guild.roles.get(role)
            if role is not None:
                self.roles.append(role)

        for role in self.roles:
            if role.id not in roles_seen:
                self.roles.pop(role.id)


class GuildEmojiState(BaseState):
    def __init__(self, client, guild):
        super().__init__(client)
        self.guild = guild

    def _add(self, data):
        emoji = self.get(data['id'])
        if emoji is not None:
            emoji._update(data)
            return emoji

        emoji = GuildEmoji.unmarshal(data, state=self, guild=self.guild)
        self._values[emoji.id] = emoji
        return emoji

    async def fetch(self, emoji_id):
        rest = self.client.rest
        data = await rest.get_guild_emoji(self.guild.id, emoji_id)
        emoji = self._add(data)
        return emoji

    async def fetch_all(self):
        rest = self.client.rest
        data = await rest.get_guild_emojis(self.guild.id)
        emojis = [self._add(emoji) for emoji in data]
        return emojis

    async def create(self, name, image, roles=None):
        rest = self.client.rest
        data = await rest.create_guild_emoji(self.guild.id, name, image, roles)
        emoji = self._add(data)
        return emoji
