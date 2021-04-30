from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseState, SnowflakeMapping
from ..objects.member import GuildMember

if TYPE_CHECKING:
    from ..objects.guild import Guild
    from ..manager import BaseManager


class GuildMemberState(BaseState):
    __container__ = SnowflakeMapping
    __guild_member_class__ = GuildMember

    def __init__(self, *, manager: BaseManager, guild: Guild):
        super().__init__(manager=manager)
        self.guild = guild

    @classmethod
    def set_guild_member_class(cls, klass: type) -> None:
        cls.__guild_class__ = klass

    def append(self, data: dict, *args, **kwargs) -> GuildMember:
        member = self.get(data['user']['id'])
        if member is not None:
            member._update(data)
        else:
            member = self.__guild_member_class__.unmarshal(
                data, state=self, guild=self.guild, *args, **kwargs)
            self[member.user.id] = member

        return member
