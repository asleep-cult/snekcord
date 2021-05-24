from .baseobject import BaseObject, BaseTemplate
from .. import rest
from ..utils import JsonField, JsonTemplate, Snowflake, _validate_keys

__all__ = ('RoleTags', 'Role')


RoleTags = JsonTemplate(
    bot_id=JsonField('bot_id', Snowflake, str),
    integration_id=JsonField('integration_id', Snowflake, str),
    premium_subscriber=JsonField('premium_subscriber')
).default_object('RoleTags')


RoleTemplate = JsonTemplate(
    name=JsonField('name'),
    color=JsonField('color'),
    hoist=JsonField('hoist'),
    position=JsonField('position'),
    permissions=JsonField('permissions'),
    managed=JsonField('managed'),
    mentionable=JsonField('mentionable'),
    tags=JsonField('tags', object=RoleTags),
    __extends__=(BaseTemplate,)
)


class Role(BaseObject, template=RoleTemplate):
    __slots__ = ('guild',)

    async def __json_init__(self, *, state, guild):
        await super().__json_init__(state=state)
        self.guild = guild

    async def modify(self, **kwargs):
        keys = rest.modify_guild_role_positions.json

        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), keys)

        data = await rest.modify_guild_role_positions.request(
            session=self.state.manager.rest,
            fmt=dict(guild_id=self.guild.id, role_id=self.id),
            json=kwargs)

        return await self.state.new(data)

    async def delete(self):
        await rest.delete_guild_role.request(
            session=self.state.manager.rest,
            fmt=dict(guild_id=self.guild.id, role_id=self.id))
