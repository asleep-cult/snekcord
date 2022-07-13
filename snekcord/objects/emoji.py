from __future__ import annotations

import typing

import attr

from ..cache import CachedModel
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined
from .base import SnowflakeObject

if typing.TYPE_CHECKING:
    from ..states import GuildIDWrapper, UserIDWrapper  # EmojiRolesView,

__all__ = ('CachedCustomEmoji', 'CustomEmoji')


class CachedCustomEmoji(CachedModel):
    """Represents a raw custom emoji within the emoji cache."""

    id: Snowflake
    guild_id: Snowflake
    name: str
    require_colons: bool
    managed: bool
    animated: bool
    available: bool
    user_id: MaybeUndefined[Snowflake]
    roles: typing.List[str]


@attr.s(kw_only=True)
class CustomEmoji(SnowflakeObject):
    """Represents a custom emoji within a guild."""

    guild: GuildIDWrapper = attr.ib()
    name: str = attr.ib()
    require_colons: bool = attr.ib()
    managed: bool = attr.ib()
    animated: bool = attr.ib()
    available: bool = attr.ib()
    user: UserIDWrapper = attr.ib()
    # roles: EmojiRolesView = attr.ib()
