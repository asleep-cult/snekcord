from .baseobject import BaseObject
from .. import rest
from ..flags import Permissions
from ..utils import _validate_keys
from ..utils.json import JsonField, JsonObject
from ..utils.snowflake import Snowflake

__all__ = ('RoleTags', 'Role')


class RoleTags(JsonObject):
    bot_id = JsonField('bot_id', Snowflake),
    integration_id = JsonField('integration_id', Snowflake)
    premium_subscriber = JsonField('premium_subscriber')


class Role(BaseObject):
    raw_name = JsonField('name')
    color = JsonField('color')
    hoist = JsonField('hoist')
    position = JsonField('position')
    permissions = JsonField('permissions', Permissions.from_value)
    managed = JsonField('managed')
    mentionable = JsonField('mentionable')
    tags = JsonField('tags', object=RoleTags)

    # For some reason '@everyone' pings everyone and the everyone role
    # is named '@everyone', this is escaped to prevent accidental pings

    def __str__(self):
        if self.id == self.guild.id:
            return f'@\u200beveryone'
        return f'@{self.raw_name}'

    @property
    def guild(self):
        return self.state.guild

    @property
    def name(self):
        if self.id == self.guild.id:
            return '@\u200beveryone'
        return self.raw_name

    @property
    def mention(self):
        if self.id == self.guild.id:
            return '@everyone'
        return f'<@&{self.id}>'

    async def modify(self, **kwargs):
        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), rest.modify_guild_role_positions.json)

        data = await rest.modify_guild_role_positions.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.guild.id, role_id=self.id),
            json=kwargs)

        return self.state.upsert(data)

    async def delete(self):
        await rest.delete_guild_role.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.guild.id, role_id=self.id))
