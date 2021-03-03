from . import structures
from .role import Role
from .state import BaseState
from .utils import _try_snowflake, undefined


class GuildMember(structures.GuildMember):
    def __init__(self, *, state, guild, user=None):
        self._state = state
        self.guild = guild
        self.user = user
        self.roles = GuildMemberRoleState(self._state._client, member=self)

    async def edit(self, **kwargs):
        rest = self._state._client.rest

        channel = kwargs.pop('channel', undefined)
        if channel is not undefined:
            channel = _try_snowflake(channel)

        data = await rest.modify_guild_member(
            self.guild.id, self.user.id, **kwargs, channel_id=channel
        )
        member = self._state._add(data)
        return member

    async def ban(self, *args, **kwargs):
        ban = await self.guild.bans.add(self, *args, **kwargs)
        return ban

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)

        if self._roles is not None:
            for role in self._roles:
                self.roles._add(role)

        if self._user is not None:
            self.user = self._state.client.users._add(self._user)


class GuildMemberState(BaseState):
    def __init__(self, client, guild):
        super().__init__(client)
        self.guild = guild

    def _add(self, data, user=None):
        if user is None:
            user = self._client.users._add(data['user'])
        member = self.get(user.id)
        if member is not None:
            member._update(data)
            return member

        member = GuildMember.unmarshal(data, state=self, guild=self.guild, user=user)
        self._values[member.user.id] = member
        return member

    async def fetch(self, member_id):
        rest = self._client.rest
        data = await rest.get_guild_member(self._guild.id, member_id)
        member = self._add(data)
        return member

    async def fetch_many(self, limit=1000, before=None):
        rest = self._client.rest
        data = await rest.get_guild_members(self._guild.id, limit, before)
        members = [self._add(member) for member in data]
        return members

    async def add(self, user, access_token, **kwargs):
        rest = self._client.rest

        user = _try_snowflake(user)

        roles = kwargs.pop('roles', undefined)
        if roles is not undefined:
            roles = [_try_snowflake(role) for role in roles]

        data = await rest.add_guild_member(
            self._guild.id, user, access_token, **kwargs, roles=roles
        )
        member = self._add(data, user=user)
        return member


class GuildMemberRoleState(BaseState):
    def __init__(self, client, member):
        super().__init__(client)
        self.member = member

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
        await rest.add_guild_member_role(self.member.guild.id, self._member.id, role.id)

    async def remove(self, role):
        rest = self._client.rest
        await rest.remove_guild_member_role(
            self._member.guild.id,
            self._member.id,
            role.id
        )
