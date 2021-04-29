from .base import BaseObject
from ..templates.channel import (
    DMChannelTemplate,
    GuildChannelTemplate,
    TextChannelTemplate,
    VoiceChannelTemplate
)

__all__ = ('GuildChannel', 'TextChannel', 'VoiceChannel', 'CategoryChannel')


class GuildChannel(BaseObject, template=GuildChannelTemplate):
    __slots__ = ('_state', 'guild')

    def __init__(self, *, state, guild):
        self._state = state
        self.guild = guild

    @property
    def mention(self):
        return f'<#{self.id}>'


class TextChannel(GuildChannel, template=TextChannelTemplate):
    pass


class VoiceChannel(GuildChannel, template=VoiceChannelTemplate):
    pass


class CategoryChannel(GuildChannel, template=GuildChannelTemplate):
    pass


class DMChannel(BaseObject, template=DMChannelTemplate):
    __slots__ = ('_state',)
