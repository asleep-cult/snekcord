from __future__ import annotations

import typing
from datetime import datetime

import attr

from .base import SnowflakeObject
from ..cache import CachedModel
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined

if typing.TYPE_CHECKING:
    from ..states import MemberRolesView

__all__ = ('Member',)


class CachedMember(CachedModel):
    user_id: Snowflake
    nick: MaybeUndefined[typing.Optional[str]]
    avatar: MaybeUndefined[typing.Optional[str]]
    role_ids: typing.List[str]
    joined_at: str
    premium_since: MaybeUndefined[typing.Optional[str]]
    deaf: bool
    mute: bool
    pending: MaybeUndefined[bool]
    communication_disabled_until: MaybeUndefined[typing.Optional[int]]


@attr.s(kw_only=True)
class Member(SnowflakeObject):
    nick: typing.Optional[str] = attr.ib()
    avatar: typing.Optional[str] = attr.ib()
    roles: MemberRolesView = attr.ib()
    joined_at: datetime = attr.ib()
    premium_since: typing.Optional[datetime] = attr.ib()
    deaf: bool = attr.ib()
    mute: bool = attr.ib()
    pending: typing.Optional[bool] = attr.ib()
    communication_disabled_until: typing.Optional[int] = attr.ib()
