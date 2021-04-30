from __future__ import annotations

from typing import Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from ..objects.guild import Guild
    from ..states.channel import ChannelState, GuildChannelState

from .base import BaseObject
from ..states.message import MessageState
from ..templates.channel import (
    DMChannelTemplate,
    GuildChannelTemplate,
    TextChannelTemplate,
    VoiceChannelTemplate
)

__all__ = ('GuildChannel', 'TextChannel', 'VoiceChannel', 'CategoryChannel')

# TODO: Have a channel base class for all channels

class GuildChannel(BaseObject, template=GuildChannelTemplate):
    __slots__ = ('_state', 'guild', 'messages')

    def __init__(self, *, state: ChannelState,
                 guild: Optional[Guild] = None) -> None:
        self._state = state
        self.guild = guild
        self.messages = MessageState(manager=state.manager, channel=self)

    @property
    def category_id(self):
        return self.parent_id

    @property
    def category(self):
        return self._state.get(self.category_id)

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
    __slots__ = ('_state', 'messages')

    def __init__(self, *, state: ChannelState):
        self._state = state
        self.messages = MessageState(manager=state.manager, channel=self)

Sendable = Union[DMChannel, TextChannel]