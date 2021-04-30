from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ..objects.guild import Guild
    from ..states.channel import ChannelState

from .base import BaseObject
from ..templates.channel import (
    DMChannelTemplate,
    GuildChannelTemplate,
    TextChannelTemplate,
    VoiceChannelTemplate
)

__all__ = ('GuildChannel', 'TextChannel', 'VoiceChannel', 'CategoryChannel')

# TODO: Have a channel base class for all channels


class GuildChannel(BaseObject, template=GuildChannelTemplate):
    __slots__ = ('guild', 'messages')

    def __init__(self, *, state: ChannelState,
                 guild: Optional[Guild] = None) -> None:
        self._state = state
        self.guild = guild
        self.messages = self._state.manager.__channel_message_state_class__(
            manager=self._state.manager, channel=self)

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
    __slots__ = ('messages',)

    def __init__(self, *, state: ChannelState):
        self._state = state
        self.messages = self._state.manager.__channel_message_state_class__(
            manager=self.manager, channel=self)


Channel = Union[GuildChannel, DMChannel]
