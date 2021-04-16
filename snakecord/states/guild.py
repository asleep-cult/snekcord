from .state import BaseState, SnowflakeMapping
from ..objects.guild import Guild


class GuildState(BaseState):
    __container__ = SnowflakeMapping

    def append(self, data: dict) -> Guild:
        guild = self.get(data['id'])
        if guild is not None:
            guild._update(data)
        else:
            guild = Guild.unmarshal(data, state=self)
            self[guild.id] = guild

        return guild
