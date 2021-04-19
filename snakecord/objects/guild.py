from .base import BaseObject
from ..states.channel import GuildChannelState
from ..templates.guild import GuildTemplate


class Guild(BaseObject, template=GuildTemplate):
    __slots__ = ('_state', 'channels')

    def __init__(self, *, state) -> None:
        self._state = state
        self.channels = GuildChannelState(
            superstate=state.manager.channels, guild=self)

    def _update(self, *args, **kwargs) -> None:
        super()._update(*args, **kwargs)

        for channel in self._channels:
            self.channels.superstate.append(channel, guild=self)

        self._channels.clear()
