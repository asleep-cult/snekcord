from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .base import BaseObject 
from ..templates.member import GuildMemberTemplate

if TYPE_CHECKING:
    from ..states.member import GuildMemberState
    from .guild import Guild
    from .user import User

__all__ = ('GuildMember',)

class GuildMember(BaseObject, template=GuildMemberTemplate):
    __slots__ = ('_state', 'guild', 'user')

    def __init__(self, *, state: GuildMemberState, guild: Guild):
        self._state = state
        self.guild = guild
        self.user: Optional[User] = None
    
    def _update(self, data: dict, *args, **kwargs):
        super()._update(data, *args, **kwargs)
        user = data.get('user')
        if user is not None:
            self.user = self._state.manager.users.append(user)
            self.id = self.user.id

    @property
    def mention(self):
        if self.user is not None:
            return self.user.mention
