from .states import ChannelState, GuildState


class BaseManager:
    __guild_state_class__ = GuildState
    __channel_state_class__ = ChannelState

    def __init__(self):
        self.guilds = self.__guild_state_class__(manager=self)
        self.chanels = self.__channel_state_class__(manager=self)

    @classmethod
    def set_guild_state_class(cls, klass) -> None:
        cls.__guild_state_class__ = klass

    @classmethod
    def set_channel_state_class(cls, klass) -> None:
        cls.__channel_state_class__ = klass
