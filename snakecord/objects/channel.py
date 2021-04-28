from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..objects.guild import Guild
    from ..states.channel import GuildChannelState

from .base import BaseObject
from ..templates.channel import (
    DMChannelTemplate,
    GuildChannelTemplate,
    TextChannelTemplate,
    VoiceChannelTemplate
)


class GuildChannel(BaseObject, template=GuildChannelTemplate):
    __slots__ = ('_state', 'guild')

    def __init__(self, *, state: GuildChannelState,
                 guild: Optional[Guild] = None) -> None:
        self._state = state
        self.guild = guild

    @property
    def category_id(self):
        return self.parent_id

    @property
    def category(self):
        return self._state.manager

    @property
    def mention(self) -> None:
        return f'<#{self.id}>'


class TextChannel(GuildChannel, template=TextChannelTemplate):
    pass


class VoiceChannel(GuildChannel, template=VoiceChannelTemplate):
    pass


class CategoryChannel(GuildChannel, template=GuildChannelTemplate):
    pass


class DMChannel(BaseObject, template=DMChannelTemplate):
    __slots__ = ('_state',)
