from __future__ import annotations

import enum
import typing

import attr

from ..cache import CachedModel
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined
from .base import SnowflakeObject, SnowflakeWrapper

__all__ = (
    'CachedUser',
    'UserFlags',
    'PremiumType',
    'User',
    'SupportsUserID',
    'UserIDWrapper',
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
class User(SnowflakeObject):
    username: str = attr.ib(eq=False)
    discriminator: str = attr.ib(eq=False)
    avatar: typing.Optional[str] = attr.ib(repr=False, eq=False)
    bot: typing.Optional[bool] = attr.ib(eq=False)
    system: typing.Optional[bool] = attr.ib(eq=False)
    mfa_enabled: typing.Optional[bool] = attr.ib(repr=False, eq=False)
    banner: typing.Optional[str] = attr.ib(repr=False, eq=False)
    accent_color: typing.Optional[int] = attr.ib(repr=False, eq=False)
    locale: typing.Optional[str] = attr.ib(repr=False, eq=False)
    verified: typing.Optional[bool] = attr.ib(repr=False, eq=False)
    email: typing.Optional[str] = attr.ib(repr=False, eq=False)
    flags: UserFlags = attr.ib(repr=False, eq=False)
    premium_type: typing.Optional[typing.Union[PremiumType, int]] = attr.ib(repr=False, eq=False)
    public_flags: UserFlags = attr.ib(repr=False, eq=False)


SupportsUserID = typing.Union[Snowflake, str, int, User]
UserIDWrapper = SnowflakeWrapper[SupportsUserID, User]
