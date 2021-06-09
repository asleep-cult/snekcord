from __future__ import annotations

import typing as t
from datetime import datetime

from .baseobject import BaseObject
from .. import rest
from ..utils import (JsonField, JsonTemplate, Permissions, Snowflake,
                     _validate_keys)

__all__ = ('GuildMember',)

if t.TYPE_CHECKING:
    from .guildobject import Guild
    from .userobject import User
    from ..states import GuildMemberState, GuildMemberRoleState
    from ..typing import Json


GuildMemberTemplate = JsonTemplate(
    nick=JsonField('nick'),
    joined_at=JsonField(
        'joined_at',
        datetime.fromisoformat,
        datetime.isoformat
    ),
    premium_since=JsonField(
        'premium_since',
        datetime.fromisoformat,
        datetime.isoformat
    ),
    deaf=JsonField('deaf'),
    mute=JsonField('mute'),
    pending=JsonField('pending'),
    _permissions=JsonField(
        'permissions',
        Permissions.from_value,
        Permissions.get_value
    ),
)


class GuildMember(BaseObject, template=GuildMemberTemplate):
    __slots__ = ('roles', 'user')

    if t.TYPE_CHECKING:
        user: User
        state: GuildMemberState
        roles: GuildMemberRoleState
        nick: t.Optional[str]
        joined_at: datetime
        premium_since: t.Optional[datetime]
        deaf: bool
        mute: bool
        pending: t.Optional[bool]
        _permissions: t.Optional[Permissions]

    def __init__(self, *, state: GuildMemberState):
        super().__init__(state=state)
        self.roles = self.state.client.get_class('GuildMemberRoleState')(
            superstate=self.guild.roles, member=self)

    @property
    def guild(self) -> Guild:
        return self.state.guild

    @property
    def permissions(self) -> Permissions:
        if self._permissions is not None:
            return self._permissions

        guild = self.guild

        if guild.owner_id == self.id:
            return Permissions.all()

        value = guild.roles.everyone.permissions.value

        for role in self.roles:
            value |= role.permissions.value

        permissions = Permissions.from_value(value)

        if permissions.administrator:
            return Permissions.all()

        return permissions

    @property
    def mention(self) -> str:
        if self.nick is not None:
            return f'<@!{self.id}>'
        return self.user.mention

    @property
    def removed(self) -> bool:
        return self.deleted

    @property
    def removed_at(self) -> t.Optional[datetime]:
        return self.deleted_at

    async def modify(self, **kwargs: t.Any) -> GuildMember:
        try:
            kwargs['channel_id'] = Snowflake.try_snowflake(
                kwargs.pop('voice_channel'))
        except KeyError:
            pass

        try:
            roles = Snowflake.try_snowflake_set(kwargs['roles'])
            kwargs['roles'] = tuple(roles)
        except KeyError:
            pass

        _validate_keys(f'{self.__class__.__name__}.modify',  # type: ignore
                       kwargs, (), rest.modify_guild_member.json)

        data = await rest.modify_guild_member.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.guild.id,
                     user_id=self.id),
            json=kwargs)

        return self.state.upsert(data)

    def update(  # type: ignore
        self, data: Json, *args: t.Any, **kwargs: t.Any
    ) -> None:
        super().update(data, *args, **kwargs)

        user = data.get('user')
        if user is not None:
            self.user = self.state.client.users.upsert(user)
            self.id = self.user.id

        roles = data.get('roles')
        if roles is not None:
            self.roles.set_keys(roles)
