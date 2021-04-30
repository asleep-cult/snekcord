from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from .base import BaseObject
from ..templates.message import MessageTemplate

if TYPE_CHECKING:
    from .guild import Guild
    from ..states.message import MessageState


class Message(BaseObject, template=MessageTemplate):
    __slots__ = ('_state', 'channel', 'author', 'member',
                 'mentions', 'role_mentions', 'channel_mentions')

    def __init__(self, *, state: MessageState):
        self._state = state
        self.channel = state.channel
        self.author = None
        self.member = None
        self.mentions = []
        self.role_mentions = []
        self.channel_mentions = []

    @property
    def guild(self) -> Optional[Guild]:
        return getattr(self.channel, 'guild', None)

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)

        if self.webhook_id is None:
            self.author = self._state.manager.users.append(self._author)

        if self._member is not None:
            self._member['user'] = self._author
            self.member = self.guild.members.append(self._member)
