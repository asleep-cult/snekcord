import typing as t

from .baseobject import BaseObject
from ..enums import PremiumType
from ..flags import UserFlags
from ..states.userstate import UserState
from ..utils.json import JsonField
from ..utils.snowflake import Snowflake


class User(BaseObject[Snowflake]):
    name: t.ClassVar[JsonField[str]]
    discriminator: t.ClassVar[JsonField[str]]
    avatar: t.ClassVar[JsonField[str]]
    bot: t.ClassVar[JsonField[bool]]
    system: t.ClassVar[JsonField[bool]]
    mfa_enabled: t.ClassVar[JsonField[bool]]
    locale: t.ClassVar[JsonField[str]]
    verified: t.ClassVar[JsonField[bool]]
    email: t.ClassVar[JsonField[str]]
    flags: t.ClassVar[JsonField[UserFlags]]
    premium_type: t.ClassVar[JsonField[PremiumType]]
    public_flags: t.ClassVar[JsonField[UserFlags]]

    state: UserState

    def __init__(self, *, state: UserState) -> None: ...

    @property
    def tag(self) -> str: ...

    @property
    def mention(self) -> str: ...
