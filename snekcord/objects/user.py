from __future__ import annotations

import enum
import typing

import attr

from .base import SnowflakeObject
from ..cache import CachedModel
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined

if typing.TYPE_CHECKING:
    from ..states import (
        SupportsUserID,
        UserState,
    )
else:
    SupportsUserID = typing.NewType('SupportsUserID', typing.Any)

__all__ = (
    'CachedUser',
    'UserFlags',
    'PremiumType',
    'User',
)


class CachedUser(CachedModel):
    id: Snowflake
    username: str
    discriminator: str
    avatar: typing.Optional[str]
    bot: MaybeUndefined[bool]
    system: MaybeUndefined[bool]
    mfa_enabled: MaybeUndefined[bool]
    banner: MaybeUndefined[typing.Optional[str]]
    accent_color: MaybeUndefined[typing.Optional[int]]
    locale: MaybeUndefined[str]
    verified: MaybeUndefined[bool]
    email: MaybeUndefined[typing.Optional[str]]
    flags: MaybeUndefined[int]
    premium_type: MaybeUndefined[int]
    public_flags: MaybeUndefined[int]


class UserFlags(enum.IntFlag):
    NONE = 0
    STAFF = 1 << 0
    PARTNER = 1 << 1
    HYPESQUAD = 1 << 2
    BUG_HUNTER_LEVEL_1 = 1 << 3
    HYPESQUAD_ONLINE_HOUSE_1 = 1 << 6
    HYPESQUAD_ONLINE_HOUSE_2 = 1 << 7
    HYPESQUAD_ONLINE_HOUSE_3 = 1 << 8
    PREMIUM_EARLY_SUPPORTER = 1 << 9
    TEAM_PSUEDO_USER = 1 << 10
    BUG_HUNTER_LEVEL_2 = 1 << 14
    VERIFIED_BOT = 1 << 16
    VERIFIED_DEVELOPER = 1 << 17
    CERTIFIED_MODERATOR = 1 << 18
    BOT_HTTP_INTERACTIONS = 1 << 19


class PremiumType(enum.IntEnum):
    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2


@attr.s(kw_only=True, slots=True, hash=True)
class User(SnowflakeObject[SupportsUserID]):
    state: UserState

    username: str = attr.ib(hash=False, eq=False)
    discriminator: str = attr.ib(hash=False, eq=False)
    avatar: typing.Optional[str] = attr.ib(repr=False, hash=False, eq=False)
    bot: typing.Optional[bool] = attr.ib(hash=False, eq=False)
    system: typing.Optional[bool] = attr.ib(hash=False, eq=False)
    mfa_enabled: typing.Optional[bool] = attr.ib(repr=False, hash=False, eq=False)
    banner: typing.Optional[str] = attr.ib(repr=False, hash=False, eq=False)
    accent_color: typing.Optional[int] = attr.ib(repr=False, hash=False, eq=False)
    locale: typing.Optional[str] = attr.ib(repr=False, hash=False, eq=False)
    verified: typing.Optional[bool] = attr.ib(repr=False, hash=False, eq=False)
    email: typing.Optional[str] = attr.ib(repr=False, hash=False, eq=False)
    flags: typing.Optional[UserFlags] = attr.ib(repr=False, hash=False, eq=False)
    premium_type: typing.Optional[typing.Union[PremiumType, int]] = attr.ib(
        repr=False, hash=False, eq=False
    )
    public_flags: typing.Optional[UserFlags] = attr.ib(repr=False, hash=False, eq=False)
