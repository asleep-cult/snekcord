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
    """The id of the guild the emoji is in."""

    name: str = attr.ib()
    """The name of the emoji."""

    require_colons: bool = attr.ib()
    """Whether the emoji must be wrapped in colons."""

    managed: bool = attr.ib()
    """Whether the emoji is managed."""

    animated: bool = attr.ib()
    """Whether the emoji is animated."""

    available: bool = attr.ib()
    """Whether the emoji is available, may be False due to loss of server boosts."""

    user: UserIDWrapper = attr.ib()
    """A wrapper for the user who created the emoji."""

    # roles: EmojiRolesView = attr.ib()
