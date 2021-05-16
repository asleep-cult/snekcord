from .baseobject import BaseObject, BaseStatelessObject
from .. import rest
from ..utils import JsonField, JsonTemplate

InviteTemplate = JsonTemplate(
    code=JsonField('code'),
    target_type=JsonField('target_type'),
    presence_count=JsonField('approximate_presence_count'),
    member_count=JsonField('approximate_member_count'),
    expires_at=JsonField('expires_at'),

    uses=JsonField('uses'),
    max_uses=JsonField('max_uses'),
    max_age=JsonField('max_age'),
    temporary=JsonField('temporary'),
    created_at=JsonField('temporary'),
)


class Invite(BaseObject, template=InviteTemplate):
    __slots__ = ('guild', 'channel', 'inviter', 'target_user',
                 'target_application')

    def __init__(self, *, state):
        super().__init__(state=state)
        self.guild = None
        self.channel = None
        self.inviter = None
        self.target_user = None
        self.target_application = None

    async def delete(self):
        await self.state.delete(self.code)

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        self.id = self.code

        guild = data.get('guild')
        if guild is not None:
            self.guild = self.state.manager.guilds.append(guild)

        channel = data.get('channel')
        if channel is not None:
            self.channel = self.state.manager.channels.append(channel)

        inviter = data.get('inviter')
        if inviter is not None:
            self.inviter = self.state.manager.users.append(inviter)

        target_user = data.get('target_user')
        if target_user is not None:
            self.target_user = self.state.manager.users.append(target_user)


class GuildVanityUrl(BaseStatelessObject):
    __slots__ = ('code',)

    def __init__(self, *, owner):
        super().__init__(owner=owner)
        self.code = None

    @property
    def invite(self):
        return self.owner.state.manager.invites.get(self.code)

    async def fetch(self):
        data = await rest.get_guild_vanity_url.request(
            session=self.owner.state.manager.rest,
            fmt=dict(guild_id=self.owner.id))

        self._update_invite(data)

        return self

    def _update_invite(self, data):
        self.code = data['code']
        self.owner.state.manager.invites.append(data)
