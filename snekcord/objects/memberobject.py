from .baseobject import BaseObject
from .. import rest
from ..utils import (JsonField, JsonTemplate, Permissions, Snowflake,
                     _validate_keys)

__all__ = ('GuildMember',)


GuildMemberTemplate = JsonTemplate(
    nick=JsonField('nick'),
    joined_at=JsonField('joined_at'),
    premium_since=JsonField('premium_since'),
    deaf=JsonField('deaf'),
    mute=JsonField('mute'),
    pending=JsonField('pending'),
    _permissions=JsonField(
        'permissions',
        Permissions.from_value,
        Permissions.get_value
    ),
)


class GuildMember(BaseObject, template=GuildMemberTemplate):
    __slots__ = ('roles', 'user')

    def __init__(self, *, state):
        super().__init__(state=state)
        self.roles = self.state.manager.get_class('GuildMemberRoleState')(
            superstate=self.guild.roles, member=self)

    @property
    def guild(self):
        return self.state.guild

    @property
    def permissions(self):
        if self._permissions is not None:
            return self._permissions

        guild = self.guild

        if guild.owner_id == self.id:
            return Permissions.all()

        value = guild.roles.everyone.permissions.value

        for role in self.roles:
            value |= role.permissions.value

        permissions = Permissions.from_value(value)

        if permissions.administrator:
            return Permissions.all()

        return permissions

    @property
    def mention(self):
        if self.nick is not None:
            return f'<@!{self.id}>'
        return self.user.mention

    @property
    def removed(self):
        return self.deleted

    @property
    def removed_at(self):
        return self.deleted_at

    async def modify(self, **kwargs):
        try:
            kwargs['channel_id'] = Snowflake.try_snowflake(
                kwargs.pop('voice_channel'))
        except KeyError:
            pass

        try:
            roles = Snowflake.try_snowflake_set(kwargs['roles'])
            kwargs['roles'] = tuple(roles)
        except KeyError:
            pass

        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), rest.modify_guild_member.json)

        data = await rest.modify_guild_member.request(
            session=self.state.manager.rest,
            fmt=dict(guild_id=self.guild.id,
                     user_id=self.id),
            json=kwargs)

        return self.state.upsert(data)

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        user = data.get('user')
        if user is not None:
            self.user = self.state.manager.users.upsert(user)
            self.id = self.user.id

        roles = data.get('roles')
        if roles is not None:
            self.roles.set_keys(roles)
