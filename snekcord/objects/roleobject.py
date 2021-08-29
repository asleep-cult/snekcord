from .baseobject import BaseObject
from .. import http
from ..flags import Permissions
from ..json import JsonField, JsonObject
from ..snowflake import Snowflake
from ..undefined import undefined

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

    async def modify(
        self, *, name=undefined, permissions=undefined, color=undefined, hoist=undefined,
        mentionable=undefined
    ):
        json = {}

        if name is not undefined:
            if name is not None:
                json['name'] = str(name)
            else:
                json['name'] = None

        if permissions is not undefined:
            if permissions is not None:
                json['permissions'] = Permissions.try_value(permissions)
            else:
                json['permissions'] = None

        if color is not undefined:
            if color is not None:
                json['color'] = int(color)
            else:
                json['color'] = None

        if hoist is not undefined:
            if hoist is not None:
                json['hoist'] = bool(hoist)
            else:
                json['hoist'] = None

        if mentionable is not undefined:
            if mentionable is not None:
                json['mentionable'] = bool(mentionable)
            else:
                json['mentionable'] = None

        data = await http.modify_guild_role.request(
            self.state.client.http, guild_id=self.guild.id, role_id=self.id, json=json
        )

        return self.state.upsert(data)

    def delete(self):
        return self.state.delete(self.id)
