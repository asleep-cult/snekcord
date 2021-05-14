from .baseobject import BaseObject
from .. import rest
from ..states.rolestate import GuildMemberRoleState
from ..templates import GuildMemberTemplate
from ..utils import Snowflake, _validate_keys


class GuildMember(BaseObject, template=GuildMemberTemplate):
    __slots__ = ('guild', 'roles')

    def __init__(self, *, state, guild):
        super().__init__(state=state)
        self.guild = guild
        self.roles = GuildMemberRoleState(superstate=self.guild.roles,
                                          member=self)

    @property
    def removed(self):
        return self.deleted

    @property
    def removed_at(self):
        return self.deleted_at

    async def modify(self, **kwargs):
        keys = rest.modify_guild_member.json

        try:
            kwargs['channel_id'] = (
                Snowflake.try_snowflake(kwargs.pop('voice_channel'))
            )
        except KeyError:
            pass

        try:
            roles = Snowflake.try_snowflake_set(kwargs['roles'])
            kwargs['roles'] = tuple(roles)
        except KeyError:
            pass

        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), keys)

        data = await rest.modify_guild_member.request(
            session=self._state.manager.rest,
            fmt=dict(guild_id=self.guild.id,
                     user_id=self.id))

        return self._state.append(data)

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        user = getattr(self, '_user', None)
        if user is not None:
            self.user = self._state.manager.users.append(user)
            self.id = self.user.id
            del self._user

        roles = getattr(self, '_roles', None)
        if roles is not None:
            self.roles.set_keys(roles)
            del self._roles
