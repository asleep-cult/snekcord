import typing

import attr

from .base import SnowflakeObject
from ..cache import CachedModel
from ..snowflake import Snowflake

__all__ = ('CustomEmoji',)


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
class CustomEmoji(SnowflakeObject):
    name: str = attr.ib()
    require_colons: bool = attr.ib()
    managed: bool = attr.ib()
    animated: bool = attr.ib()
    available: bool = attr.ib()
    user_id: Snowflake = attr.ib()
    roles = attr.ib()

    @property
    def guild(self):
        return self.state.guild
