import re
from urllib.parse import quote

from .baseobject import BaseObject
from .. import rest
from ..utils import JsonArray, JsonField, Snowflake

try:
    import snekcord.emojis as _emojis
except ImportError:
    _emojis = None


__all__ = ('GuildEmoji', 'BuiltinEmoji')

CUSTOM_EMOJI_RE = re.compile(r'<?(?P<animated>a)?:(?P<name>.{2,32}):(?P<id>\d{17,19})>?')

BUILTIN_EMOJIS_BY_SURROGATES = {}
BUILTIN_EMOJIS_BY_NAME = {}


class BaseEmoji:
    def to_reaction(self):
        raise NotImplementedError

    def to_media(self):
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
    role_ids = JsonField('roles', Snowflake)
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

    def to_partial(self):
        return PartialGuildEmoji(
            client=self.state.client, id=self.id, name=self.name, animated=self.animated
        )

    def update(self, data):
        super().update(data)

        if 'user' in data:
            self.user = self.state.client.users.update(data['user'])


class _BaseBuiltinEmoji(BaseEmoji):
    @property
    def id(self):
        return self.surrogates

    def to_reaction(self):
        return quote(self.surrogates)


class BuiltinEmoji(_BaseBuiltinEmoji):
    def __init__(self, *, category, data):
        self.category = category

        self.surrogates, self.names, self.unicode_version, diversity_children = data

        self.diversity_children = []
        for child in diversity_children:
            self.diversity_children.append(BuiltinEmoji(category=category, data=child))

    def __str__(self):
        return self.surrogates.decode()

    @property
    def id(self):
        return self.surrogates

    @property
    def name(self):
        return self.names[0]

    def to_reaction(self):
        return quote(self.surrogates)

    def _store(self):
        BUILTIN_EMOJIS_BY_SURROGATES[self.surrogates] = self

        for name in self.names:
            BUILTIN_EMOJIS_BY_NAME[name] = self

        for child in self.diversity_children:
            child._store()


class PartialBuiltinEmoji(_BaseBuiltinEmoji):
    def __init__(self, *, surrogates):
        self.surrogates = surrogates


def _get_builtin_emoji(surrogates):
    emoji = BUILTIN_EMOJIS_BY_SURROGATES.get(surrogates)
    if emoji is None:
        emoji = PartialBuiltinEmoji(surrogates=surrogates)
    return emoji


def _resolve_emoji(state, emoji):
    if isinstance(emoji, BaseEmoji):
        return emoji

    if isinstance(emoji, int):
        return state.get(emoji)

    if isinstance(emoji, str):
        match = CUSTOM_EMOJI_RE.match(emoji)
        if match is not None:
            emoj_id = Snowflake(match.group('id'))

            emoji = state.get(emoj_id)
            if emoji is not None:
                return emoji

            return PartialGuildEmoji(
                client=state.client, id=emoj_id, name=match.group('name'),
                animated=bool(match.group('animated'))
            )

        builtin_emoji = BUILTIN_EMOJIS_BY_NAME.get(emoji)

        if builtin_emoji is not None:
            return builtin_emoji

        emoji = emoji.encode()

    if isinstance(emoji, bytes):
        return _get_builtin_emoji(emoji)

    raise TypeError(f'{emoji!r} is not a valid emoji')


if _emojis is not None:
    for category, emojis in _emojis.ALL_CATEGORIES.items():
        for data in emojis:
            BuiltinEmoji(category=category, data=data)._store()
