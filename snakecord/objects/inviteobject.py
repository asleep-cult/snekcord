from .baseobject import BaseObject
from .. import rest
from ..utils import JsonField, JsonObject, JsonTemplate

__all__ = ('Invite', 'GuildVanityUrl')


InviteTemplate = JsonTemplate(
    id=JsonField('code'),
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

    def __json_init__(self, *, state):
        super().__json_init__(state=state)
        self.guild = None
        self.channel = None
        self.inviter = None
        self.target_user = None
        self.target_application = None

    @property
    def code(self):
        return self.id

    async def delete(self):
        await self.state.delete(self.code)

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

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


GuildVanityUrlTemplate = JsonTemplate(
    code=JsonField('code')
)


class GuildVanityUrl(JsonObject, template=GuildVanityUrlTemplate):
    __slots__ = ('guild',)

    def __json_init__(self, *, guild):
        self.guild = guild

    @property
    def invite(self):
        return self.guild.state.manager.invites.get(self.code)

    async def fetch(self):
        data = await rest.get_guild_vanity_url.request(
            session=self.guild.state.manager.rest,
            fmt=dict(guild_id=self.guild.id))

        self.update(data)

        return self

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        data['guild'] = self.guild.to_idict()
        self.guild.state.manager.invites.append(data)
