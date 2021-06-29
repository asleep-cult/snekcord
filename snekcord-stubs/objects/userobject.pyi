import typing as t

from .baseobject import BaseObject
from ..states.userstate import UserState
from ..utils.bitset import Bitset, Flag
from ..utils.enum import Enum
from ..utils.json import JsonField
from ..utils.snowflake import Snowflake


class UserFlags(Bitset):
    discord_employee: t.ClassVar[Flag]
    partnered_server_owner: t.ClassVar[Flag]
    hypesquad_events: t.ClassVar[Flag]
    bug_hunter_level_1: t.ClassVar[Flag]
    mfa_sms: t.ClassVar[Flag]
    premium_promo_dismissed: t.ClassVar[Flag]
    house_bravery: t.ClassVar[Flag]
    house_brilliance: t.ClassVar[Flag]
    house_balance: t.ClassVar[Flag]
    early_supporter: t.ClassVar[Flag]
    team_user: t.ClassVar[Flag]
    has_unread_urgent_message: t.ClassVar[Flag]
    bug_hunter_level_2: t.ClassVar[Flag]
    verified_bot: t.ClassVar[Flag]
    early_verified_bot_developer: t.ClassVar[Flag]
    discord_certified_moderator: t.ClassVar[Flag]


class PremiumType(Enum[int]):
    NONE: t.ClassVar[int]
    NITRO_CLASSIC: t.ClassVar[int]
    NITRO: t.ClassVar[int]


class User(BaseObject[Snowflake]):
    name: JsonField[str]
    discriminator: JsonField[str]
    avatar: JsonField[str]
    bot: JsonField[bool]
    system: JsonField[bool]
    mfa_enabled: JsonField[bool]
    locale: JsonField[str]
    verified: JsonField[bool]
    email: JsonField[str]
    flags: JsonField[UserFlags]
    premium_type: JsonField[PremiumType]
    public_flags: JsonField[UserFlags]

    state: UserState

    def __init__(self, *, state: UserState) -> None: ...

    @property
    def tag(self) -> str: ...

    @property
    def mention(self) -> str: ...
