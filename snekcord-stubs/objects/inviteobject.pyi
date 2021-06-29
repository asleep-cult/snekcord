from __future__ import annotations

from datetime import datetime

from .baseobject import BaseObject
from .channelobject import GuildChannel
from .guildobject import Guild
from .userobject import User
from ..states.invitestate import InviteState
from ..utils.enum import Enum
from ..utils.json import JsonObject, JsonTemplate


class InviteTargetType(Enum[int]):
    STREAM = 1
    EMBEDDED_APPLICATION = 2


InviteTemplate: JsonTemplate = ...


class Invite(BaseObject[str], template=InviteTemplate):
    target_type: InviteTargetType
    presence_count: int
    member_count: int
    expires_at: int
    uses: int
    max_uses: int
    max_age: int
    temporary: bool
    created_at: datetime

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


GuildVanityURLTemplate: JsonTemplate = ...


class GuildVanityURL(JsonObject, template=GuildVanityURLTemplate):
    code: str

    guild: Guild

    def __init__(self, *, guild: Guild) -> None: ...

    @property
    def invite(self) -> Invite | None: ...

    async def fetch(self) -> GuildVanityURL: ...
