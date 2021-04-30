from .base import BaseState, SnowflakeMapping, WeakValueSnowflakeMapping
from ..objects.guild import Guild


class GuildState(BaseState):
    __container__ = SnowflakeMapping
    __recycled_container__ = WeakValueSnowflakeMapping
    __guild_class__ = Guild

    @classmethod
    def set_guild_class(cls, klass: type):
        cls.__guild_class__ = klass

    def append(self, data: dict, *args, **kwargs) -> Guild:
        guild = self.get(data['id'])
        if guild is not None:
            guild._update(data)
        else:
            guild = self.__guild_class__.unmarshal(
                data, state=self, *args, **kwargs)
            guild.cache()

        return guild
