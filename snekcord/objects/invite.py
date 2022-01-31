from __future__ import annotations

import enum
import typing
from datetime import datetime

import attr

from .base import CodeObject
from ..cache import CachedModel
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined

if typing.TYPE_CHECKING:
    from ..states import (
        InviteState,
        SupportsInviteCode,
    )
else:
    SupportsInviteCode = typing.NewType('SupportsInviteCode', typing.Any)


class CachedInvite(CachedModel):
    code: str
    guild_id: MaybeUndefined[str]
    channel_id: typing.Optional[str]
    inviter_id: MaybeUndefined[str]
    target_type: MaybeUndefined[int]
    target_user_id: MaybeUndefined[str]
    target_application_id: MaybeUndefined[str]
    expires_at: MaybeUndefined[typing.Optional[str]]
    uses: int
    max_uses: int
    max_age: int
    temporary: bool
    created_at: str


class InviteTargetType(enum.IntEnum):
    STREAM = 1
    EMBEDDED_APPLICATION = 2


@attr.s(kw_only=True)
class Invite(CodeObject[SupportsInviteCode]):
    state: InviteState

    guild_id: Snowflake = attr.ib()
    channel_id: Snowflake = attr.ib()
    inviter_id: Snowflake = attr.ib()
    target_type: InviteTargetType = attr.ib()
    target_id: Snowflake = attr.ib()
    expires_at: datetime = attr.ib()


@attr.s(kw_only=True)
class RESTInvite(Invite):
    presence_count: int = attr.ib()
    member_count: int = attr.ib()
