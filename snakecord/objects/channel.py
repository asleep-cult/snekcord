from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Union

from .base import BaseObject
from ..connections.rest import (
    RestFuture,
    delete_channel
)
from ..templates.channel import (
    DMChannelTemplate,
    GuildChannelTemplate,
    TextChannelTemplate,
    VoiceChannelTemplate
)

if TYPE_CHECKING:
    from .guild import Guild
    from ..states.channel import ChannelState

__all__ = ('GuildChannel', 'TextChannel', 'VoiceChannel', 'CategoryChannel')

# TODO: Have a channel base class for all channels


class GuildChannel(BaseObject, template=GuildChannelTemplate):
    _state: ChannelState
    __slots__ = ('guild', 'messages', '_state')

    def __init__(self, *, state: ChannelState,
                 guild: Optional[Guild] = None) -> None:
        super().__init__(state=state)
        self.guild = guild
        self.messages = self._state.manager.__channel_message_state_class__(
            manager=self._state.manager, channel=self)

    @property
    def category(self):
        return self._state.get(self.category_id)

    @property
    def mention(self) -> str:
        return f'<#{self.id}>'

    def delete(self) -> RestFuture:
        return delete_channel.request(
            session=self._state.manager.rest,
            fmt={'channel_id': self.id}
        )


class TextChannel(GuildChannel, template=TextChannelTemplate):
    pass


class VoiceChannel(GuildChannel, template=VoiceChannelTemplate):
    pass


class CategoryChannel(GuildChannel, template=GuildChannelTemplate):
    pass


class DMChannel(BaseObject, template=DMChannelTemplate):
    _state: ChannelState
    __slots__ = ('messages',)

    def __init__(self, *, state: ChannelState):
        self._state = state
        self.messages = self._state.manager.__channel_message_state_class__(
            manager=state.manager, channel=self)


Channel = Union[GuildChannel, DMChannel]
