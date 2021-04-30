from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseObject
from ..templates.role import RoleTemplate

if TYPE_CHECKING:
    from ..objects.guild import Guild
    from ..states.role import RoleState


class Role(BaseObject, template=RoleTemplate):
    __slots__ = ('guild', '_state')

    def __init__(self, *, state: RoleState, guild: Guild):
        self.guild = guild
        self._state = state
