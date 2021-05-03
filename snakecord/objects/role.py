from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseObject
from ..templates.role import RoleTemplate

if TYPE_CHECKING:
    from ..objects.guild import Guild
    from ..states.role import GuildRoleState


class Role(BaseObject, template=RoleTemplate):
    __slots__ = ('guild',)

    def __init__(self, *, state: GuildRoleState, guild: Guild):
        self.guild = guild
        self._state = state
