from __future__ import annotations

import typing as t

from .baseobject import BaseObject
from .. import rest
from ..utils import JsonField, JsonObject, JsonTemplate

__all__ = ('Invite', 'GuildVanityURL')

if t.TYPE_CHECKING:
    from ..objects import DMChannel, GuildChannel, Guild, User
    from ..states import InviteState
    from ..typing import Json

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

    if t.TYPE_CHECKING:
        id: str  # type: ignore
        state: InviteState  # type: ignore
        guild: t.Optional[Guild]
        channel: t.Union[DMChannel, GuildChannel, None]
        inviter: t.Optional[User]
        target_user: t.Optional[User]
        target_application: None  # ???

    def __init__(self, *, state: InviteState) -> None:
        super().__init__(state=state)  # type: ignore
        self.guild = None
        self.channel = None
        self.inviter = None
        self.target_user = None
        self.target_application = None

    @property
    def code(self) -> str:
        return self.id

    async def delete(self) -> None:
        await rest.delete_invite.request(
                session=self.state.client.rest,
                fmt=dict(code=self.code))

    def update(  # type: ignore
        self, data: Json,
        *args: t.Any, **kwargs: t.Any
    ) -> None:
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

    if t.TYPE_CHECKING:
        code: str
        guild: Guild

    def __init__(self, *, guild: Guild) -> None:
        self.guild = guild

    @property
    def invite(self) -> t.Optional[Invite]:
        return self.guild.state.client.invites.get(self.code)

    async def fetch(self) -> GuildVanityURL:
        data = await rest.get_guild_vanity_url.request(
            session=self.guild.state.client.rest,
            fmt=dict(guild_id=self.guild.id))

        self.update(data)

        return self

    def update(  # type: ignore
        self, data: Json, *args: t.Any, **kwargs: t.Any
    ) -> None:
        super().update(data, *args, **kwargs)

        if 'code' in data:
            invite = self.guild.state.client.invites.upsert(data)
            invite.guild = self.guild
