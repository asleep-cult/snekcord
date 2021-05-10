from .baseobject import BaseObject
from .. import rest
from ..state.rolestate import GuildMemberRoleState
from ..templates import GuildMemberTemplate
from ..utils import Snowflake, _validate_keys


class GuildMember(BaseObject, template=GuildMemberTemplate):
    def __init__(self, *, state, guild):
        super().__init__(state=state)
        self.guild = guild
        self.roles = GuildMemberRoleState(superstate=self.guild.roles,
                                          member=self)

    async def modify(self, **kwargs):
        keys = rest.modify_guild_member

        try:
            kwargs['channel_id'] = (
                Snowflake.try_snowflake(kwargs.pop('voice_channel'))
            )
        except KeyError:
            pass

        try:
            roles = {
                Snowflake.try_snowflake(r) for r in kwargs.pop('roles')
            }
            kwargs['roles'] = list(roles)
        except KeyError:
            pass

        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), keys)

        data = await rest.modify_guild_member.request(
            session=self._state.manager.rest,
            fmt=dict(guild_id=self.guild.id,
                     user_id=self.member.id))

        return self.append(data)

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        if self._user:
            self.user = self._state.manager.users.append(self._user)
            self._user.clear()

        self.roles.set_keys(self._roles)
        self._roles.clear()
