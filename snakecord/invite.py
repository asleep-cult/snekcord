from .bases import BaseState
from .utils import JsonStructure, JsonField, JSON
from typing import Optional

INVITE_BASE_URL = 'https://discord.com/invite/'


class Invite(JsonStructure):
    __json_fields__ = {
        'code': JsonField('code'),
        '_guild': JsonField('guild'),
        '_channel': JsonField('channel'),
        'guild_id': JsonField('guild_id'),
        'channel_id': JsonField('channel_id'),
        '_inviter': JsonField('inviter'),
        '_target_user': JsonField('target_user'),
        'target_user_type': JsonField('target_user_type'),
        'approximate_presence_count': JsonField('approximate_presence_count'),
        'approximate_member_count': JsonField('approximate_member_count'),

        # metadata
        'uses': JsonField('uses'),
        'max_uses': JsonField('max_uses'),
        'temporary': JsonField('temporary'),
        'created_at': JsonField('created_at'),
    }

    code: str
    _guild: Optional[JSON]
    _channel: Optional[JSON]
    guild_id: int
    channel_id: int
    _inviter: Optional[JSON]
    _target_user: Optional[JSON]
    target_user_type: Optional[int]
    approximate_presence_count: Optional[int]
    approximate_member_count: Optional[int]
    uses: Optional[int]
    max_uses: Optional[int]
    temporary: Optional[bool]
    created_at: Optional[str]

    def __init__(self, state=None):
        self._state = state

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)

        if self._guild is not None:
            self.guild = self._state._client.guilds._add(self._guild)
        else:
            self.guild = self._state._client.guilds.get(self.guild_id)

        if self._channel is not None:
            self.channel = self._state._client.channels.add(self._channel)
        else:
            self.channel = self._state._client.channels.get(self.guild_id)

        if self._inviter is not None:
            self.inviter = self._state._client.users._add(self._inviter)
        if self._target_user is not None:
            self.target_user = self._state._client.users._add(
                self._target_user
            )

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
            invite._update(data, set_default=False)
            return invite
        invite = self.__state_class__.unmarshal(data, state=self)
        self._values[invite.code] = invite
        return invite

    async def fetch(self, code, with_counts=False):
        rest = self._client.rest
        resp = await rest.get_invite(code, with_counts)
        data = await resp.json()
        invite = self._add(data)
        return invite

    async def delete(self, code):
        rest = self._client.rest
        await rest.delete_invite(code)


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
        return invites


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
        return invites

    async def create(
        self,
        *,
        max_age=None,
        max_uses=None,
        temporary=None,
        unique=None,
        target_user=None,
        target_user_type=None
    ):
        rest = self._invite_state._client.rest

        if target_user is not None:
            target_user = target_user.id

        resp = await rest.create_channel_invite(
            max_age=max_age, max_uses=max_uses,
            temporary=temporary, unique=unique,
            target_user_id=target_user,
            target_user_type=target_user_type
        )
        data = await resp.json()
        invite = self._invite_state._add(data)
        return invite


class PartialInvite(JsonStructure):
    __json_fields__ = {
        'code': JsonField('code'),
        'uses': JsonField('uses'),
    }

    code: str
    uses: int
