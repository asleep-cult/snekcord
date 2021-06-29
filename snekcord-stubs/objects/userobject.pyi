from .baseobject import BaseObject
from ..states.userstate import UserState
from ..utils.bitset import Bitset, Flag
from ..utils.enum import Enum
from ..utils.json import JsonTemplate
from ..utils.snowflake import Snowflake


class UserFlags(Bitset):
    discord_employee = Flag(0)
    partnered_server_owner = Flag(1)
    hypesquad_events = Flag(2)
    bug_hunter_level_1 = Flag(3)
    mfa_sms = Flag(4)
    premium_promo_dismissed = Flag(5)
    house_bravery = Flag(6)
    house_brilliance = Flag(7)
    house_balance = Flag(8)
    early_supporter = Flag(9)
    team_user = Flag(10)
    has_unread_urgent_message = Flag(13)
    bug_hunter_level_2 = Flag(14)
    verified_bot = Flag(16)
    early_verified_bot_developer = Flag(17)
    discord_certified_moderator = Flag(18)


class PremiumType(Enum[int]):
    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2


UserTemplate: JsonTemplate = ...


class User(BaseObject[Snowflake], template=UserTemplate):
    name: str
    discriminator: str
    avatar: str
    bot: bool
    system: bool
    mfa_enabled: bool
    locale: str
    verified: bool
    email: str
    flags: UserFlags
    premium_type: PremiumType
    public_flags: UserFlags

    state: UserState

    def __init__(self, *, state: UserState) -> None: ...

    @property
    def tag(self) -> str: ...

    @property
    def mention(self) -> str: ...
