from . import structures
from .state import BaseState, BaseSubState
from .utils import _try_snowflake, undefined

INVITE_BASE_URL = 'https://discord.com/invite/'


class Invite(structures.Invite):
    __slots__ = (
        *structures.Invite.__json_fields__, '_state', 'guild',
        'channel', 'inviter', 'target_user'
    )

    def __init__(self, *, state=None):
        self._state = state
        self.guild = None
        self.channel = None
        self.inviter = None
        self.target_user = None

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)

        if self._guild is not None:
            self.guild = self._state.client.guilds.append(self._guild)
        else:
            self.guild = self._state.client.guilds.get(self.guild_id)

        if self._channel is not None:
            self.channel = self._state.client.channels.append(self._channel)
        else:
            self.channel = self._state.client.channels.get(self.channel_id)

        if self._inviter is not None:
            self.inviter = self._state.client.users.append(self._inviter)
        if self._target_user is not None:
            self.target_user = self._state.client.users.append(self._target_user)

    @property
    def url(self):
        return INVITE_BASE_URL + self.code

    async def delete(self):
        await self._state.delete(self.code)


class InviteState(BaseState):
    def append(self, data):
        invite = self.get(data['code'])
        if invite is not None:
            invite._update(data)
            return invite

        invite = Invite.unmarshal(data, state=self)
        self._items[invite.code] = invite
        return invite

    async def fetch(self, code, with_counts=False):
        rest = self.client.rest
        data = await rest.get_invite(code, with_counts)
        invite = self.append(data)
        return invite

    async def delete(self, code):
        rest = self.client.rest
        await rest.delete_invite(code)


class GuildInviteState(BaseSubState):
    def __init__(self, *, superstate, guild):
        super().__init__(superstate=superstate)
        self.guild = guild

    def _check_relation(self, item):
        return isinstance(item, Invite) and item.guild == self.guild

    async def fetch_all(self):
        rest = self.superstate.client.rest
        data = await rest.get_guild_invites(self.guild.id)
        invites = [self.append(invite) for invite in data]
        return invites


class ChannelInviteState(BaseSubState):
    def __init__(self, *, superstate, channel):
        super().__init__(superstate=superstate)
        self.channel = channel

    def _check_relation(self, item):
        return isinstance(item, Invite) and item.channel == self.channel

    async def fetch_all(self):
        rest = self.superstate.client.rest
        data = await rest.get_channel_invites(self._channel.id)
        invites = [self.append(invite) for invite in data]
        return invites

    async def create(self, **kwargs):
        rest = self.superstate.client.rest

        target_user = kwargs.pop('target_user', undefined)
        if target_user is not undefined:
            target_user = _try_snowflake(target_user)

        data = await rest.create_channel_invite(**kwargs, target_user_id=target_user)
        invite = self.append(data)
        return invite
