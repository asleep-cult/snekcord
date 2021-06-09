from __future__ import annotations

import typing as t

from .baseobject import BaseObject, BaseTemplate
from .. import rest
from ..utils import (JsonField, JsonTemplate, Permissions, Snowflake,
                     _validate_keys)

__all__ = ('RoleTags', 'Role')

if t.TYPE_CHECKING:
    from .guildobject import Guild
    from ..states import RoleState

RoleTags = JsonTemplate(
    bot_id=JsonField('bot_id', Snowflake, str),
    integration_id=JsonField('integration_id', Snowflake, str),
    premium_subscriber=JsonField('premium_subscriber')
).default_object('RoleTags')


RoleTemplate = JsonTemplate(
    raw_name=JsonField('name'),
    color=JsonField('color'),
    hoist=JsonField('hoist'),
    position=JsonField('position'),
    permissions=JsonField(
        'permissions',
        Permissions.from_value,
        Permissions.get_value
    ),
    managed=JsonField('managed'),
    mentionable=JsonField('mentionable'),
    tags=JsonField('tags', object=RoleTags),
    __extends__=(BaseTemplate,)
)


class Role(BaseObject, template=RoleTemplate):
    if t.TYPE_CHECKING:
        state: RoleState
        raw_name: str
        color: int
        hoist: bool
        position: int
        permissions: Permissions
        managed: bool
        mentionable: bool
        tags: t.Optional[RoleTags]

    @property
    def guild(self) -> Guild:
        return self.state.guild

    # For some reason '@everyone' pings everyone and the everyone role
    # is named '@everyone', this is escaped to prevent accidental pings

    def __str__(self) -> str:
        if self.id == self.guild.id:
            return f'@\u200beveryone'
        return f'@{self.raw_name}'

    @property
    def name(self) -> str:
        if self.id == self.guild.id:
            return '@\u200beveryone'
        return self.raw_name

    @property
    def mention(self) -> str:
        if self.id == self.guild.id:
            return '@everyone'
        return f'<@&{self.id}>'

    async def modify(self, **kwargs: t.Any) -> Role:
        _validate_keys(f'{self.__class__.__name__}.modify',  # type: ignore
                       kwargs, (), rest.modify_guild_role_positions.json)

        data = await rest.modify_guild_role_positions.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.guild.id, role_id=self.id),
            json=kwargs)

        return self.state.upsert(data)

    async def delete(self) -> None:
        await rest.delete_guild_role.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.guild.id, role_id=self.id))
