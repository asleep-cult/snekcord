from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseObject
from ..templates.guild import GuildTemplate

if TYPE_CHECKING:
    from ..states.guild import GuildState

__all__ = ('Guild',)


class Guild(BaseObject, template=GuildTemplate):
    __slots__ = ('channels', 'members', 'emojis', 'roles')

    def __init__(self, *, state: GuildState) -> None:
        self._state = state
        self.channels = self._state.manager.__guild_channel_state_class__(
            superstate=state.manager.channels, guild=self)
        self.emojis = self._state.manager.__guild_emoji_state_class__(
            manager=state.manager, guild=self)
        self.members = self._state.manager.__guild_member_state_class__(
            manager=state.manager, guild=self)
        self.roles = self._state.manager.__guild_role_state_class__(
            manager=state.manager, guild=self)

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
