from .bases import BaseObject, BaseState
from .utils import JsonField, JsonArray, Snowflake, JSON

from typing import Optional, List


class GuildEmoji(BaseObject):
    __json_fields__ = {
        'name': JsonField('name'),
        '_roles': JsonArray('roles'),
        '_user': JsonField('user'),
        'required_colons': JsonField('required_colons'),
        'managed': JsonField('managed'),
        'animated': JsonField('animated'),
        'available': JsonField('available'),
    }

    id: Optional[Snowflake]
    name: Optional[str]
    _roles: Optional[List[JSON]]
    _user: Optional[JSON]
    required_colons: Optional[bool]
    managed: Optional[bool]
    animated: Optional[bool]
    available: Optional[bool]

    def __init__(self, state, guild):
        self._state = state
        self.guild = guild

    def __str__(self):
        if self.id is None:
            return self.name
        elif self.animated:
            return '<a:%s:%s>' % (self.name, self.id)
        else:
            return '<:%s:%s>' % (self.name, self.id)

    def __repr__(self):
        return '<GuildEmoji String: %r, Roles: %s, Guild: %s>' % (
            str(self), self.roles, self.guild)

    async def delete(self):
        rest = self._state._client.rest
        await rest.delete_guild_emoji(self.guild.id, self.id)

    async def edit(self, name=None, roles=None):
        rest = self._state._client.rest
        await rest.modify_guild_emoji(self.guild.id, self.id, name, roles)

    def to_dict(self):
        dct = super().to_dict()

        if self.user is not None:
            dct['user'] = self.user.to_dict()

        dct['roles'] = [role.id for role in self.roles]

        return dct

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)
        self.user = None
        self.roles = []

        if self._user is not None:
            self.user = self._state._client.users._add(self._user)

        for role in self._roles:
            role = self.guild.roles.get(role)
            if role is not None:
                self.roles.append(role)


class GuildEmojiState(BaseState):
    __state_class__ = GuildEmoji

    def __init__(self, client, guild):
        super().__init__(client)
        self._guild = guild

    def _add(self, data):
        emoji = self.get(data.get('id'))
        if emoji is not None:
            emoji._update(data, set_default=False)
            return emoji
        emoji = self.__state_class__.unmarshal(
            data,
            state=self,
            guild=self._guild
        )
        self._values[emoji.id] = emoji
        return emoji

    async def fetch(self, emoji_id):
        rest = self._client.rest
        resp = await rest.get_guild_emoji(self._guild.id, emoji_id)
        data = await resp.data()
        emoji = self._add(data)
        return emoji

    async def fetch_all(self):
        rest = self._client.rest
        resp = await rest.get_guild_emojis(self._guild.id)
        data = await resp.data()
        emojis = []
        for emoji in data:
            emoji = self._add(emoji)
            emojis.append(emoji)
        return emojis

    async def create(self, name, image, roles=None):
        rest = self._client.rest
        resp = await rest.create_guild_emoji(
            self._guild.id,
            name,
            image,
            roles
        )
        data = await resp.json()
        emoji = self._add(data)
        return emoji
