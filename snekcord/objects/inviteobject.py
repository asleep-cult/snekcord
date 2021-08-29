from datetime import datetime

from .baseobject import BaseObject
from .. import http
from ..enums import InviteTargetType
from ..json import JsonField, JsonObject

__all__ = ('Invite', 'GuildVanityURL')


class Invite(BaseObject):
    __slots__ = ('guild', 'channel', 'inviter', 'target_user', 'target_application')

    id = JsonField('code')
    target_type = JsonField('target_type', InviteTargetType.try_enum)
    presence_count = JsonField('approximate_presence_count')
    member_count = JsonField('approximate_member_count')
    expires_at = JsonField('expires_at')

    uses = JsonField('uses')
    max_uses = JsonField('max_uses')
    max_age = JsonField('max_age')
    temporary = JsonField('temporary')
    created_at = JsonField('temporary', datetime.fromisoformat)

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

    def delete(self):
        return self.state.delete(self.code)

    def update(self, data):
        super().update(data)

        if 'guild' in data:
            self.guild = self.state.client.guilds.upsert(data['guild'])

        if 'channel' in data:
            self.channel = self.state.client.channels.upsert(data['channel'])

        if 'inviter' in data:
            self.inviter = self.state.client.users.upsert(data['inviter'])

        if 'target_user' in data:
            self.target_user = self.state.client.users.upsert(data['target_user'])

        return self


class GuildVanityURL(JsonObject):
    __slots__ = ('guild',)

    code = JsonField('code')
    uses = JsonField('uses')

    def __init__(self, *, guild):
        self.guild = guild

    @property
    def invite(self):
        return self.guild.state.client.invites.get(self.code)

    async def fetch(self):
        data = await http.get_guild_vanity_url.request(
            self.guild.state.client.http, guild_id=self.guild.id
        )

        return self.update(data)

    def update(self, data):
        super().update(data)

        if 'code' in data:
            invite = self.guild.state.client.invites.upsert(data)
            invite.guild = self.guild

        return self
