from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseObject
from ..templates.emoji import GuildEmojiTemplate

if TYPE_CHECKING:
    from .guild import Guild
    from ..states.emoji import GuildEmojiState


class GuildEmoji(BaseObject, template=GuildEmojiTemplate):
    __slots__ = ('guild',)

    def __init__(self, *, state: GuildEmojiState, guild: Guild):
        super().__init__(state=state)
        self.guild = guild
