from .bases import BaseState

from .utils import (
    JsonStructure,
    JsonField
)

INVITE_BASE_URL = 'https://discord.com/invite/'

class Invite(JsonStructure):
    code = JsonField('code')
    _guild = JsonField('guild')
    _channel = JsonField('channel')
    guild_id = JsonField('guild_id')
    channel_id = JsonField('channel_id')
    _inviter = JsonField('inviter')
    _target_user = JsonField('target_user')
    target_user_type = JsonField('target_user_type')
    approximate_presence_count = JsonField('approximate_presence_count')
    approximate_member_count = JsonField('approximate_member_count')

    #metadata
    uses = JsonField('uses')
    max_uses = JsonField('max_uses')
    temporary = JsonField('temporary')
    create_at = JsonField('created_at')

    def __init__(self, state=None):
        self._state = state
        if self._guild is not None:
            self.guild = self._state._client.guilds._add(self._guild)
            self.channel = self._state._client.channels._add(self._channel)
        else:
            self.guild = self._state._client.guilds.get(self.guild_id)
            self.channel = self._state._client.channels.get(self.channel_id)
        if self._inviter is not None:
            self.inviter = self._state._client.users._add(self._inviter)
        if self._target_user is not None:
            self.target_user = self._state._client.users._add(self._target_user)
        
        del self._guild
        del self._channel
        del self._target_user

    @property
    def url(self):
        return INVITE_BASE_URL + self.code

    async def delete(self):
        await self._state.delet(self.code)

class InviteState(BaseState):
    def _add(self, data):
        invite = self.get(data['code'])
        if invite is not None:
            invite._update(data)
            return invite
        invite = Invite.unmarshal(data, state=self)
        self._values[invite.code] = invite
        return invite

    async def fetch(self, code, with_counts=False):
        rest = self._client.rest
        resp = await rest.get_invite(code, with_counts)
        data = await resp.json()
        invite = self._add(invite)
        return invite

    async def delete(self, code):
        rest = self._client.rest
        resp = await rest.delete_invite(code)


# GuildInviteState and ChannelInviteState essentialy wrap InviteState
# their __iter__ methods yield all invites associated with them
# and their fetch_all methods fetch all invites associated with them
# but they are actually stored in InvteState, Invites being cached
# is not garunteed because they are only received through the gateway
# when they are created and can only be retrieved through fetching after that

class GuildInviteState:
    def __init__(self, invite_state, guild):
        self._invite_state = invite_state
        self._guild = guild

    def __iter__(self):
        for invite in self._invite_state:
            if invite.guild == self._guild:
                yield invite

    async def fetch_all(self):
        rest = self._invite_state._client.rest
        resp = await rest.get_guild_invites(self._guild.id)
        data = await resp.json()
        invites = []
        for invite in data:
            invite = self._invite_state._add(invite)
            invites.append(invite)
        return invite

class ChannelInviteState:
    def __init__(self, invite_state, channel):
        self._invite_state = invite_state
        self._channel = channel

    def __iter__(self):
        for invite in self._invite_state:
            if invite.channel == self._channel:
                yield invite

    async def fetch_all(self):
        rest = self._invite_state._client.rest
        resp = await rest.get_channel_invites(self._channel.id)
        data = await resp.json()
        invites = []
        for invite in data:
            invite = self._invite_state._add(invite)
            invites.append(invite)
        return invite