from __future__ import annotations

import typing as t
from datetime import datetime

from .baseobject import BaseObject
from .channelobject import GuildChannel
from .guildobject import Guild
from .userobject import User
from ..states.invitestate import InviteState
from ..utils.enum import Enum
from ..utils.json import JsonField, JsonObject


class InviteTargetType(Enum[int]):
    STREAM: t.ClassVar[int]
    EMBEDDED_APPLICATION: t.ClassVar[int]


class Invite(BaseObject[str]):
    target_type: JsonField[InviteTargetType]
    presence_count: JsonField[int]
    member_count: JsonField[int]
    expires_at: JsonField[int]
    uses: JsonField[int]
    max_uses: JsonField[int]
    max_age: JsonField[int]
    temporary: JsonField[bool]
    created_at: JsonField[datetime]

    state: InviteState
    guild: Guild | None
    channel: GuildChannel | None
    inviter: User | None
    target_user: User | None
    target_application: None

    def __init__(self, *, state: InviteState) -> None: ...

    @property
    def code(self) -> str: ...

    async def delete(self) -> None: ...


class GuildVanityURL(JsonObject):
    code: JsonField[str]

    guild: Guild

    def __init__(self, *, guild: Guild) -> None: ...

    @property
    def invite(self) -> Invite | None: ...

    async def fetch(self) -> GuildVanityURL: ...
