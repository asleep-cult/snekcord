from __future__ import annotations

from typing import Any, List, Optional, TYPE_CHECKING

from .base import BaseObject
from ..templates.message import MessageTemplate

if TYPE_CHECKING:
    from .guild import Guild
    from ..states.message import ChannelMessageState


class Message(BaseObject, template=MessageTemplate):
    content: str
    __slots__ = ('channel', 'author', 'member',
                 'mentions', 'role_mentions', 'channel_mentions')

    def __init__(self, *, state: ChannelMessageState):
        self._state = state
        self.channel = state.channel
        self.author = None
        self.member = None
        self.mentions: List[Any] = []
        self.role_mentions: List[Any] = []
        self.channel_mentions: List[Any] = []

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
