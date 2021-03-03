from .bases import BaseState
from .utils import JsonStructure, JsonField, JSON
from .role import Role

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .guild import Guild


class GuildMember(JsonStructure):
    __json_slots__ = (
        '_user', 'nick', '_roles', 'joined_at', 'premium_since',
        'deaf', 'mute', 'pending', '_state', 'guild', 'user'
    )

    __json_fields__ = {
        '_user': JsonField('user'),
        'nick': JsonField('nick'),
        '_roles': JsonField('roles'),
        'joined_at': JsonField('joined_at'),
        'premium_since': JsonField('premium_since'),
        'deaf': JsonField('deaf'),
        'mute': JsonField('mute'),
        'pending': JsonField('pending'),
    }

    _user: Optional[JSON]
    nick: str
    _roles: list
    joined_at: str
    premium_since: Optional[str]
    deaf: bool
    mute: bool
    pending: Optional[bool]

    def __init__(
        self,
        *,
        state: 'GuildMemberState',
        guild: 'Guild',
        user=None
    ):
        self._state: GuildMemberState = state
        self.guild = guild
        self.user = user

    async def edit(
        self,
        nick=None,
        roles=None,
        mute=None,
        deaf=None,
        channel=None
    ):
        rest = self._state._client.rest

        if channel is not None:
            channel = channel.id

        resp = await rest.modify_guild_member(
            self.guild.id, self.user.id, roles=roles,
            mute=mute, deaf=deaf, channel=channel
        )
        data = await resp.json()
        member = self._state._add(data)
        return member

    async def ban(self, *, reason=None, delete_message_days=None):
        ban = await self.guild.bans.add(
            self,
            reason=reason,
            delete_message_days=delete_message_days
        )
        return ban

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)
        self.roles = GuildMemberRoleState(self._state._client, member=self)

        if self._roles is not None:
            for role in self._roles:
                self.roles._add(role)

        if self._user is not None:
            self.user = self._state._client.users._add(self._user)

        del self._user
        del self._roles


class GuildMemberRoleState(BaseState):
    def __init__(self, client, member):
        super().__init__(client)
        self._member = member

    def _add(self, role):
        if isinstance(role, Role):
            self._values[role.id] = role
            return role
        role = self._member.guild.roles.get(role)
        if role is not None:
            self._values[role.id] = role
        return role

    async def add(self, role):
        rest = self._client.rest
        await rest.add_guild_member_role(
            self._member.guild.id,
            self._member.id,
            role.id
        )

    async def remove(self, role):
        rest = self._client.rest
        await rest.remove_guild_member_role(
            self._member.guild.id,
            self._member.id,
            role.id
        )


class GuildMemberState(BaseState):
    __state_class__ = GuildMember

    def __init__(self, client, guild):
        super().__init__(client)
        self._guild = guild

    def _add(self, data, user=None):
        if user is None:
            user = self._client.users._add(data['user'])
        member = self.get(user.id)
        if member is not None:
            member._update(data)
            return member
        member = self.__state_class__.unmarshal(
            data,
            state=self,
            guild=self._guild,
            user=user
        )
        self._values[member.user.id] = member
        self._client.events.member_cache(member)
        return member

    async def fetch(self, member_id):
        rest = self._client.rest
        data = await rest.get_guild_member(self._guild.id, member_id)
        member = self._add(data)
        return member

    async def fetch_many(self, limit=1000, before=None):
        rest = self._client.rest
        resp = await rest.get_guild_members(self._guild.id, limit, before)
        data = await resp.json()
        members = []
        for member in data:
            member = self._add(member)
            members.append(member)
        return members

    async def add(
        self,
        user,
        access_token,
        *,
        nick=None,
        roles=None,
        mute=None,
        deaf=None
    ):
        rest = self._client.rest
        if roles is not None:
            roles = {role.id for role in roles}
        resp = await rest.add_guild_member(
            self._guild.id, user.id, access_token,
            nick=nick, roles=roles, mute=mute,
            deaf=deaf
        )
        data = await resp.json()
        member = self._add(data, user=user)
        return member
