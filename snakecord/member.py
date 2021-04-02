from . import structures
from .role import Role
from .state import BaseState
from .utils import _try_snowflake, undefined


class GuildMember(structures.GuildMember):
    __slots__ = (
        '_state', 'guild', 'user', 'roles'
    )

    def __init__(self, *, state, guild, user=None):
        self._state = state
        self.guild = guild
        self.user = user
        self.roles = GuildMemberRoleState(
            client=self._state.client, member=self)

    async def edit(self, **kwargs):
        rest = self._state.client.rest

        channel = kwargs.pop('channel', undefined)
        if channel is not undefined:
            channel = _try_snowflake(channel)

        data = await rest.modify_guild_member(
            self.guild.id, self.user.id, **kwargs, channel_id=channel
        )
        member = self._state.append(data)
        return member

    async def ban(self, *args, **kwargs):
        ban = await self.guild.bans.add(self, *args, **kwargs)
        return ban

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)

        if self._roles is not None:
            for role in self._roles:
                self.roles.append(role)

        if self._user is not None:
            self.user = self._state.client.users.append(self._user)


class GuildMemberState(BaseState):
    def __init__(self, *, client, guild):
        super().__init__(client=client)
        self.guild = guild

    def append(self, data, user=None):
        if user is None:
            user = self.client.users.append(data['user'])

        member = self.get(user.id)
        if member is not None:
            member._update(data)
            return member

        member = GuildMember.unmarshal(data, state=self, guild=self.guild, user=user)
        self._items[member.user.id] = member
        return member

    async def fetch(self, member_id):
        rest = self.client.rest
        data = await rest.get_guild_member(self.guild.id, member_id)
        member = self.append(data)
        return member

    async def fetch_many(self, limit=1000, before=None):
        rest = self.client.rest
        data = await rest.get_guild_members(self.guild.id, limit, before)
        members = [self.append(member) for member in data]
        return members

    async def add(self, user, access_token, **kwargs):
        rest = self.client.rest

        user = _try_snowflake(user)

        roles = kwargs.pop('roles', undefined)
        if roles is not undefined:
            roles = [_try_snowflake(role) for role in roles]

        data = await rest.add_guild_member(
            self.guild.id, user, access_token, **kwargs, roles=roles
        )
        member = self.append(data, user=user)
        return member


class GuildMemberRoleState(BaseState):
    def __init__(self, *, client, member):
        super().__init__(client=client)
        self.member = member

    def append(self, role):
        if isinstance(role, Role):
            self._items[role.id] = role
            return role

        role = self.member.guild.roles.get(role)
        if role is not None:
            self._items[role.id] = role
        return role

    async def add(self, role):
        rest = self.client.rest
        role = _try_snowflake(role)
        await rest.add_guild_member_role(self.member.guild.id, self.member.id, role)

    async def remove(self, role):
        rest = self.client.rest
        role = _try_snowflake(role)
        await rest.remove_guild_member_role(self.member.guild.id, self.member.id, role)
