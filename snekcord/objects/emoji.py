import typing

import attr

from .base import SnowflakeObject
from ..cache import CachedModel

if typing.TYPE_CHECKING:
    from ..states import (
        EmojiRolesView,
        EmojiState,
        SupportsEmojiID,
        UserIDWrapper,
    )

__all__ = ('CachedCustomEmoji', 'CustomEmoji')


class CachedCustomEmoji(CachedModel):
    id: str
    name: str
    require_colons: bool
    managed: bool
    animated: bool
    available: bool
    user_id: str
    role_ids: typing.List[str]


@attr.s(kw_only=True)
class CustomEmoji(SnowflakeObject[SupportsEmojiID]):
    state: EmojiState

    name: str = attr.ib()
    require_colons: bool = attr.ib()
    managed: bool = attr.ib()
    animated: bool = attr.ib()
    available: bool = attr.ib()
    user: UserIDWrapper = attr.ib()
    roles: EmojiRolesView = attr.ib()
