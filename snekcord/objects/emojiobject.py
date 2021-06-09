from __future__ import annotations

import typing as t

from urllib.parse import quote

from .baseobject import BaseObject, BaseTemplate
from .. import rest
from ..utils import (JsonArray, JsonField, JsonTemplate, Snowflake,
                     _validate_keys)

if t.TYPE_CHECKING:
    from .guildobject import Guild
    from .userobject import User
    from ..states import GuildEmojiState
    from ..typing import Json

    _Emoji = t.Tuple[bytes, tuple[str], float, t.Tuple[t.Any, ...]]

    ALL_CATEGORIES: dict[str, t.List[_Emoji]]

try:
    from snekcord.emojis import ALL_CATEGORIES  # type: ignore
except ImportError:
    ALL_CATEGORIES = {}  # type: ignore


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
    __slots__ = ('guild', 'user')

    if t.TYPE_CHECKING:
        guild: Guild
        user: t.Optional[User]
        name: t.Optional[str]
        role_ids: t.Optional[t.List[Snowflake]]
        required_colons: t.Optional[bool]
        managed: t.Optional[bool]
        animated: t.Optional[bool]
        available: t.Optional[bool]

    def __init__(self, *, state: GuildEmojiState, guild: Guild) -> None:
        super().__init__(state=state)
        self.guild = guild
        self.user = None

    def __str__(self) -> str:
        if self.animated:
            return f'<a:{self.name}:{self.id}>'
        return f'<:{self.name}:{self.id}>'

    @property
    def roles(self):
        if self.role_ids is not None:
            for role_id in self.role_ids:
                yield self.guild.roles.get(role_id)

    async def modify(self, **kwargs: t.Any) -> GuildEmoji:
        try:
            roles = Snowflake.try_snowflake_set(kwargs['roles'])
            kwargs['roles'] = tuple(roles)
        except KeyError:
            pass

        _validate_keys(f'{self.__class__.__name__}.modify',  # type: ignore
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

    def update(  # type: ignore
        self, data: Json, *args: t.Any, **kwargs: t.Any
    ) -> None:
        super().update(data, *args, **kwargs)

        user = data.get('user')
        if user is not None:
            self.user = self.state.client.users.upsert(user)


class BuiltinEmoji:
    def __init__(self, category: str, data: _Emoji):
        self.category = category

        self.surrogates = data[0]
        self.names = data[1]
        self.unicode_version = data[2]

        self.diversity_children: t.List[BuiltinEmoji] = []
        for child in data[3]:
            self.diversity_children.append(BuiltinEmoji(category, child))

    @property
    def id(self):
        return self.surrogates

    def store(self, cache: t.Dict[bytes, BuiltinEmoji]) -> None:
        cache[self.surrogates] = self

        for child in self.diversity_children:
            child.store(cache)

    def to_reaction(self) -> str:
        return quote(self.surrogates)


BUILTIN_EMOJIS: t.Dict[bytes, BuiltinEmoji] = {}

for category, emojis in ALL_CATEGORIES.items():
    for data in emojis:
        emoji = BuiltinEmoji(category, data)
        emoji.store(BUILTIN_EMOJIS)
