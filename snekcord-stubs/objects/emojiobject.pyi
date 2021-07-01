from __future__ import annotations

import typing as t

from .baseobject import BaseObject
from .guildobject import Guild
from .userobject import User
from ..states.emojistate import EmojiState
from ..utils import JsonArray, JsonField, Snowflake

T = t.TypeVar('T')
_Emoji = tuple[bytes, tuple[str], float, tuple['_Emoji', ...]]

ALL_CATEGORIES: dict[str, _Emoji]

BUILTIN_EMOJIS: dict[bytes, BuiltinEmoji]


class GuildEmoji(BaseObject[Snowflake]):
    name: t.ClassVar[JsonField[str]]
    role_ids: t.ClassVar[JsonArray[Snowflake]]
    required_colons: t.ClassVar[JsonField[bool]]
    managed: t.ClassVar[JsonField[bool]]
    animated: t.ClassVar[JsonField[bool]]
    available: t.ClassVar[JsonField[bool]]

    state: EmojiState
    user: User | None

    def __init__(self, *, state: EmojiState) -> None: ...

    @property
    def guild(self) -> Guild: ...

    @property
    def roles(self) -> t.Generator[Guild, None, None]: ...

    async def modify(self, **kwargs: t.Any) -> GuildEmoji: ...

    async def delete(self) -> None: ...

    def to_reaction(self) -> str: ...


class BuiltinEmoji:
    category: str
    surrogates: bytes
    names: tuple[str, ...]
    unicode_version: float
    diversity_children: list[BuiltinEmoji]

    def __init__(self, category: str, data: _Emoji) -> None: ...

    @property
    def id(self) -> bytes: ...

    def to_reaction(self) -> str: ...
