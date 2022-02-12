from __future__ import annotations

import typing

import attr

from .base import SnowflakeObject
from ..cache import CachedModel
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined

if typing.TYPE_CHECKING:
    from ..states import (
        # EmojiRolesView,
        GuildIDWrapper,
        SupportsEmojiID,
        UserIDWrapper,
    )
else:
    SupportsEmojiID = typing.NewType('SupportsEmojiID', typing.Any)

__all__ = ('CachedCustomEmoji', 'CustomEmoji')


class CachedCustomEmoji(CachedModel):
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
class CustomEmoji(SnowflakeObject[SupportsEmojiID]):
    guild: GuildIDWrapper = attr.ib()
    name: str = attr.ib()
    require_colons: bool = attr.ib()
    managed: bool = attr.ib()
    animated: bool = attr.ib()
    available: bool = attr.ib()
    user: UserIDWrapper = attr.ib()
    # roles: EmojiRolesView = attr.ib()
