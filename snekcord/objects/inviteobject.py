from datetime import datetime

from .baseobject import BaseObject
from .. import rest
from ..utils.enum import Enum
from ..utils.json import JsonField, JsonObject, JsonTemplate

__all__ = ('Invite', 'GuildVanityURL')


class InviteTargetType(Enum[int]):
    STREAM = 1
    EMBEDDED_APPLICATION = 2


InviteTemplate = JsonTemplate(
    id=JsonField('code'),
    target_type=JsonField(
        'target_type',
        InviteTargetType.get_enum,
        InviteTargetType.get_value
    ),
    presence_count=JsonField('approximate_presence_count'),
    member_count=JsonField('approximate_member_count'),
    expires_at=JsonField('expires_at'),

    uses=JsonField('uses'),
    max_uses=JsonField('max_uses'),
    max_age=JsonField('max_age'),
    temporary=JsonField('temporary'),
    created_at=JsonField(
        'temporary',
        datetime.fromisoformat,
        datetime.isoformat
    ),
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

    @property
    def code(self):
        return self.id

    async def delete(self):
        await rest.delete_invite.request(
                session=self.state.client.rest,
                fmt=dict(code=self.code))

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        guild = data.get('guild')
        if guild is not None:
            self.guild = self.state.client.guilds.upsert(guild)

        channel = data.get('channel')
        if channel is not None:
            self.channel = self.state.client.channels.upsert(channel)

        inviter = data.get('inviter')
        if inviter is not None:
            self.inviter = self.state.client.users.upsert(inviter)

        target_user = data.get('target_user')
        if target_user is not None:
            self.target_user = self.state.client.users.upsert(target_user)


GuildVanityURLTemplate = JsonTemplate(
    code=JsonField('code')
)


class GuildVanityURL(JsonObject, template=GuildVanityURLTemplate):
    __slots__ = ('guild',)

    def __init__(self, *, guild):
        self.guild = guild

    @property
    def invite(self):
        return self.guild.state.client.invites.get(self.code)

    async def fetch(self):
        data = await rest.get_guild_vanity_url.request(
            session=self.guild.state.client.rest,
            fmt=dict(guild_id=self.guild.id))

        self.update(data)

        return self

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        if 'code' in data:
            invite = self.guild.state.client.invites.upsert(data)
            invite.guild = self.guild
