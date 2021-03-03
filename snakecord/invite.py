from . import structures
from .state import BaseState
from .utils import _try_snowflake, undefined

INVITE_BASE_URL = 'https://discord.com/invite/'


class Invite(structures.Invite):
    def __init__(self, state=None):
        self._state = state

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)

        if self._guild is not None:
            self.guild = self._state.client.guilds._add(self._guild)
        else:
            self.guild = self._state.client.guilds.get(self.guild_id)

        if self._channel is not None:
            self.channel = self._state.client.channels.add(self._channel)
        else:
            self.channel = self._state.client.channels.get(self.guild_id)

        if self._inviter is not None:
            self.inviter = self._state.client.users._add(self._inviter)
        if self._target_user is not None:
            self.target_user = self._state.client.users._add(self._target_user)

    @property
    def url(self):
        return INVITE_BASE_URL + self.code

    async def delete(self):
        await self._state.delet(self.code)


class InviteState(BaseState):
    __state_class__ = Invite

    def _add(self, data):
        invite = self.get(data['code'])
        if invite is not None:
            invite._update(data)
            return invite

        invite = Invite.unmarshal(data, state=self)
        self._values[invite.code] = invite
        return invite

    async def fetch(self, code, with_counts=False):
        rest = self.client.rest
        data = await rest.get_invite(code, with_counts)
        invite = self._add(data)
        return invite

    async def delete(self, code):
        rest = self.client.rest
        await rest.delete_invite(code)


# GuildInviteState and ChannelInviteState essentialy wrap InviteState
# their __iter__ methods yield all invites associated with them
# and their fetch_all methods fetch all invites associated with them
# but they are actually stored in InvteState, Invites being cached
# is not garunteed because they are only received through the gateway
# when they are created and can only be retrieved through fetching after that

class GuildInviteState(InviteState):
    def __init__(self, invite_state, guild):
        self._items = invite_state._items
        self.client = invite_state.client
        self.guild = guild
        self._invite_state = invite_state

    def __iter__(self):
        for invite in self._invite_state:
            if invite.guild == self.guild:
                yield invite

    async def fetch_all(self):
        rest = self._invite_state.client.rest
        data = await rest.get_guild_invites(self.guild.id)
        invites = [self._add(invite) for invite in data]
        return invites


class ChannelInviteState(InviteState):
    def __init__(self, invite_state, channel):
        self._items = invite_state._items
        self.client = invite_state.client
        self.channel = channel
        self._invite_state = invite_state

    def __iter__(self):
        for invite in self._invite_state:
            if invite.channel == self.channel:
                yield invite

    async def fetch_all(self):
        rest = self._invite_state.client.rest
        data = await rest.get_channel_invites(self._channel.id)
        invites = [self._add(invite) for invite in data]
        return invites

    async def create(self, **kwargs):
        rest = self._invite_state.client.rest

        target_user = kwargs.pop('target_user', undefined)
        if target_user is not undefined:
            target_user = _try_snowflake(target_user)

        data = await rest.create_channel_invite(**kwargs, target_user_id=target_user)
        invite = self._add(data)
        return invite
