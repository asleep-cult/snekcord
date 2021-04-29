from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseObject
from ..states.channel import GuildChannelState
from ..states.emoji import GuildEmojiState
from ..states.member import GuildMemberState
from ..states.role import RoleState
from ..templates.guild import GuildTemplate

if TYPE_CHECKING:
    from ..states.guild import GuildState

__all__ = ('Guild',)

class Guild(BaseObject, template=GuildTemplate):
    __slots__ = ('_state', 'channels', 'members', 'emojis', 'roles')

    def __init__(self, *, state: GuildState) -> None:
        self._state = state
        self.channels = GuildChannelState(superstate=state.manager.channels, guild=self)
        self.emojis = GuildEmojiState(manager=state.manager, guild=self)
        self.members = GuildMemberState(manager=state.manager, guild=self)
        self.roles = RoleState(manager=state.manager, guild=self)

    def _update(self, *args, **kwargs) -> None:
        super()._update(*args, **kwargs)

        for channel in self._channels:
            self.channels.superstate.append(channel, guild=self)
        
        for member in self._members:
            self.members.append(member)
        
        for emoji in self._emojis:
            self.emojis.append(emoji)
        
        for role in self._roles:
            self.roles.append(role)

        self._channels.clear()
        self._members.clear()
        self._emojis.clear()
        self._roles.clear()
