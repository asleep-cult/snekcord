from datetime import datetime

from .baseobject import BaseObject
from .. import rest
from ..clients.client import ClientClasses
from ..flags import Permissions
from ..json import JsonField
from ..snowflake import Snowflake
from ..undefined import undefined

__all__ = ('GuildMember',)


class GuildMember(BaseObject):
    __slots__ = ('roles', 'user')

    nick = JsonField('nick')
    joined_at = JsonField('joined_at', datetime.fromisoformat)
    premium_since = JsonField('premium_since', datetime.fromisoformat)
    deaf = JsonField('deaf')
    mute = JsonField('mute')
    pending = JsonField('pending')

    def __init__(self, *, state):
        super().__init__(state=state)

        self.user = None

        self.roles = ClientClasses.GuildMemberRoleState(superstate=self.guild.roles, member=self)

    def __str__(self):
        return str(self.user)

    @property
    def guild(self):
        return self.state.guild

    @property
    def permissions(self):
        if 'permissions' in self._json_data_:
            return Permissions.from_value(self._json_data_['permissions'])

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

    async def modify(
        self, *, nick=undefined, roles=undefined, mute=undefined, deaf=undefined,
        voice_channel=undefined
    ):
        json = {}

        if nick is not undefined:
            if nick is not None:
                json['nick'] = str(nick)
            else:
                json['nick'] = None

        if roles is not undefined:
            if roles is not None:
                json['roles'] = Snowflake.try_snowflake_many(roles)
            else:
                json['roles'] = None

        if mute is not undefined:
            if mute is not None:
                json['mute'] = bool(mute)
            else:
                json['mute'] = None

        if deaf is not undefined:
            if deaf is not None:
                json['deaf'] = bool(deaf)
            else:
                json['deaf'] = None

        if voice_channel is not undefined:
            if voice_channel is not None:
                json['channel_id'] = Snowflake.try_snowflake(voice_channel)
            else:
                json['channel_id'] = None

        data = await rest.modify_guild_member.request(
            self.state.client.rest, guild_id=self.guild.id, user_id=self.id, json=json
        )

        return self.state.upsert(data)

    def remove(self):
        return self.state.remove(self.id)

    def update(self, data):
        super().update(data)

        if 'user' in data:
            self.user = self.state.client.users.upsert(data['user'])
            self._json_data_['id'] = self.user._json_data_['id']

        if 'roles' in data:
            for role in data['roles']:
                self.roles.add_key(Snowflake(role))

        return self
