from urllib.parse import quote

from .baseobject import BaseObject
from .. import rest
from ..exceptions import PartialObjectError
from ..clients.client import ClientClasses
from ..utils import JsonArray, JsonField, Snowflake, undefined


__all__ = ('CustomEmoji', 'PartialCustomEmoji', 'UnicodeEmoji', 'PartialUnicodeEmoji')


class BaseEmoji:
    @property
    def image(self):
        raise NotImplementedError

    def to_reaction(self):
        raise NotImplementedError


class _BaseCustomEmoji(BaseEmoji):
    def __str__(self):
        if self.animated:
            return f'<a:{self.name}:{self.id}>'
        return f'<:{self.name}:{self.id}>'

    def to_reaction(self):
        return quote(f'{self.name}:{self.id}')


class PartialCustomEmoji(_BaseCustomEmoji):
    def __init__(self, *, client, id, name, animated):
        self.client = client
        self.id = id
        self.name = name
        self.animated = animated

    async def fetch_guild(self):
        data = await rest.get_emoji_guild.request(
            self.client.rest, {'emoji_id': self.id}
        )

        return self.client.guilds.upsert(data)


class CustomEmoji(BaseObject, _BaseCustomEmoji):
    __slots__ = ('user',)

    name = JsonField('name')
    role_ids = JsonArray('roles', Snowflake)
    required_colons = JsonField('required_colons')
    managed = JsonField('managed')
    animated = JsonField('animated')
    available = JsonField('available')
    # This field will never come from Discord, it is injected into the object by the library.
    guild_id = JsonField('guild_id', Snowflake)

    def __init__(self, *, state):
        super().__init__(state=state)
        self.user = None

    @property
    def guild(self):
        try:
            return self.state.client.guilds.get(self.guild_id)
        except PartialObjectError:
            return None

    async def fetch_guild(self):
        if self.guild is not None:
            return await self.guild.fetch()

        data = await rest.get_emoji_guild.request(
            self.state.client.rest, {'emoji_id': self.id}
        )

        guild = self.state.client.guilds.upsert(data)
        self._json_data_['guild_id'] = guild._json_data_['id']
        return guild

    def get_roles(self):
        for role_id in self.role_ids:
            try:
                yield self.guild.roles[role_id]
            except KeyError:
                continue

    async def modify(self, *, name=None, roles=undefined):
        json = {}

        if name is not None:
            json['name'] = str(name)

        if roles is not undefined:
            if roles is not None:
                json['roles'] = Snowflake.try_snowflake_many(roles)
            else:
                json['roles'] = None

        data = await rest.modify_guild_emoji.request(
            self.state.client.rest,
            {'guild_id': self.guild.id, 'emoji_id': self.id},
            json=json
        )

        return self.state.upsert(data)

    def delete(self):
        return self.state.delete(self.id)

    def to_partial(self):
        return PartialCustomEmoji(
            client=self.state.client, id=self.id, name=self.name, animated=self.animated
        )

    def _delete(self):
        super()._delete()

        if self.guild is not None:
            self.guild.emojis.remove_key(self.id)

    def update(self, data):
        super().update(data)

        if 'user' in data:
            self.user = self.state.client.users.update(data['user'])

        return self


class _BaseUnicodeEmoji(BaseEmoji):
    @property
    def unicode(self):
        return self.surrogates.encode()

    @property
    def id(self):
        return self.surrogates

    def to_reaction(self):
        return quote(self.surrogates)


class UnicodeEmoji(_BaseUnicodeEmoji):
    def __init__(self, *, category, data):
        self.category = category

        self.surrogates, self.names, self.unicode_version, diversity_children = data

        self.diversity_children = []

        for child in diversity_children:
            self.diversity_children.append(
                ClientClasses.UnicodeEmoji(category=category, data=child)
            )

    def __str__(self):
        return f':{self.name}:'

    @property
    def name(self):
        return self.names[0]

    def to_reaction(self):
        return quote(self.surrogates)

    def _store(self, surrogates, names):
        surrogates[self.surrogates] = self

        for name in self.names:
            names[name] = self

        for child in self.diversity_children:
            child._store(surrogates, names)


class PartialUnicodeEmoji(_BaseUnicodeEmoji):
    def __init__(self, *, surrogates):
        self.surrogates = surrogates

    def __str__(self):
        return self.unicode
