from __future__ import annotations

import typing as t
from datetime import datetime

from .baseobject import BaseObject
from .channelobject import GuildChannel
from .guildobject import Guild
from .userobject import User
from ..enums import InviteTargetType
from ..states.invitestate import InviteState
from ..utils import JsonField, JsonObject


class Invite(BaseObject[str]):
    target_type: t.ClassVar[JsonField[InviteTargetType]]
    presence_count: t.ClassVar[JsonField[int]]
    member_count: t.ClassVar[JsonField[int]]
    expires_at: t.ClassVar[JsonField[int]]
    uses: t.ClassVar[JsonField[int]]
    max_uses: t.ClassVar[JsonField[int]]
    max_age: t.ClassVar[JsonField[int]]
    temporary: t.ClassVar[JsonField[bool]]
    created_at: t.ClassVar[JsonField[datetime]]

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
    code: t.ClassVar[JsonField[str]]

    guild: Guild

    def __init__(self, *, guild: Guild) -> None: ...

    @property
    def invite(self) -> Invite | None: ...

    async def fetch(self) -> GuildVanityURL: ...
