import enum
import typing

from ..snowflake import Snowflake

if typing.TYPE_CHECKING:
    from typing_extensions import NotRequired


class UserPremiumType(enum.IntEnum):
    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2


class RawUser(typing.TypedDict):
    id: Snowflake
    username: str
    discriminator: str
    avatar: typing.Optional[str]
    bot: NotRequired[bool]
    system: NotRequired[bool]
    mfa_enabled: NotRequired[bool]
    banner: NotRequired[typing.Optional[str]]
    accent_colot: NotRequired[typing.Optional[int]]
    locale: NotRequired[str]
    verified: NotRequired[bool]
    email: NotRequired[typing.Optional[str]]
    flags: NotRequired[int]
    premium_type: NotRequired[typing.Union[UserPremiumType, int]]
