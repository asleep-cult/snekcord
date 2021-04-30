from __future__ import annotations

from typing import Optional, TYPE_CHECKING

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

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)

        if self._user is not None:
            self.user = self._state.manager.users.append(self._user)

    @property
    def mention(self):
        if self.nick is None:
            return self.user.mention
        return f'<@!{self.id}>'
