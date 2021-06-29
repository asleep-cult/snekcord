from urllib.parse import quote

from .baseobject import BaseObject, BaseTemplate
from .. import rest
from ..utils import _validate_keys
from ..utils.json import JsonArray, JsonField, JsonTemplate
from ..utils.snowflake import Snowflake

try:
    from snekcord.emojis import ALL_CATEGORIES
except ImportError:
    ALL_CATEGORIES = {}


__all__ = ('GuildEmoji', 'BuiltinEmoji')


GuildEmojiTemplate = JsonTemplate(
    name=JsonField('name'),
    role_ids=JsonArray('roles', Snowflake, str),
    required_colons=JsonField('required_colons'),
    managed=JsonField('managed'),
    animated=JsonField('animated'),
    available=JsonField('available'),
    __extends__=(BaseTemplate,)
)


class GuildEmoji(BaseObject, template=GuildEmojiTemplate):
    __slots__ = ('user',)

    def __init__(self, *, state):
        super().__init__(state=state)
        self.user = None

    def __str__(self):
        if self.animated:
            return f'<a:{self.name}:{self.id}>'
        return f'<:{self.name}:{self.id}>'

    @property
    def guild(self):
        return self.state.guild

    @property
    def roles(self):
        if self.role_ids is not None:
            for role_id in self.role_ids:
                yield self.guild.roles.get(role_id)

    async def modify(self, **kwargs):
        try:
            roles = Snowflake.try_snowflake_set(kwargs['roles'])
            kwargs['roles'] = tuple(roles)
        except KeyError:
            pass

        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), rest.modify_guild_emoji.json)

        data = await rest.modify_guild_emoji.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.guild.id, emoji_id=self.id),
            json=kwargs)

        self.update(data)

        return self

    async def delete(self):
        await rest.delete_guild_emoji.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.guild.id, emoji_id=self.id))

    def to_reaction(self):
        return quote(f'{self.name}:{self.id}')

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        user = data.get('user')
        if user is not None:
            self.user = self.state.client.users.upsert(user)


class BuiltinEmoji:
    def __init__(self, category, data):
        self.category = category

        self.surrogates = data[0]
        self.names = data[1]
        self.unicode_version = data[2]

        self.diversity_children = []
        for child in data[3]:
            self.diversity_children.append(BuiltinEmoji(category, child))

    @property
    def id(self):
        return self.surrogates

    def _store(self, cache):
        cache[self.surrogates] = self

        for child in self.diversity_children:
            child._store(cache)

    def to_reaction(self) -> str:
        return quote(self.surrogates)


BUILTIN_EMOJIS = {}

for category, emojis in ALL_CATEGORIES.items():
    for data in emojis:
        emoji = BuiltinEmoji(category, data)
        emoji._store(BUILTIN_EMOJIS)
