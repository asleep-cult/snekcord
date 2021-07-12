from urllib.parse import quote

from .baseobject import BaseObject
from .. import rest
from ..utils import JsonArray, JsonField, Snowflake, undefined


__all__ = ('GuildEmoji', 'PartialGuildEmoji', 'UnicodeEmoji', 'PartialUnicodeEmoji')


class BaseEmoji:
    @property
    def image(self):
        raise NotImplementedError

    def to_reaction(self):
        raise NotImplementedError


class _BaseGuildEmoji(BaseEmoji):
    def __str__(self):
        if self.animated:
            return f'<a:{self.name}:{self.id}>'
        return f'<:{self.name}:{self.id}>'

    def to_reaction(self):
        return quote(f'{self.name}:{self.id}')


class PartialGuildEmoji(_BaseGuildEmoji):
    def __init__(self, *, client, id, name, animated):
        self.client = client
        self.id = id
        self.name = name
        self.animated = animated


class GuildEmoji(BaseObject, _BaseGuildEmoji):
    __slots__ = ('user',)

    name = JsonField('name')
    role_ids = JsonArray('roles', Snowflake)
    required_colons = JsonField('required_colons')
    managed = JsonField('managed')
    animated = JsonField('animated')
    available = JsonField('available')

    def __init__(self, *, state):
        super().__init__(state=state)
        self.user = None

    @property
    def guild(self):
        return self.state.guild

    def iterroles(self):
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
        return PartialGuildEmoji(
            client=self.state.client, id=self.id, name=self.name, animated=self.animated
        )

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
            self.diversity_children.append(UnicodeEmoji(category=category, data=child))

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
