from datetime import datetime

from .baseobject import BaseObject
from .. import rest
from ..resolvers import resolve_image_data
from ..utils import JsonField, Snowflake, undefined

__all__ = ('GuildTemplate',)


class GuildTemplate(BaseObject):
    id = JsonField('code')
    name = JsonField('name')
    description = JsonField('description')
    usage_count = JsonField('usage_count')
    creator_id = JsonField('creator_id', Snowflake)
    created_at = JsonField('created_at', datetime.fromisoformat)
    updated_at = JsonField('updated_at', datetime.fromisoformat)
    source_guild_id = JsonField('source_guild_id', Snowflake)
    # if someone actually needs this field to be more user friendly...
    # ever... make an issue https://github.com/asleep-cult/snekcord/issues
    serialized_source_guild = JsonField('serialized_source_guild')
    dirty = JsonField('is_dirty')

    @property
    def code(self):
        return self.id

    @property
    def creator(self):
        return self.state.client.users.get(self.creator_id)

    @property
    def source_guild(self):
        return self.state.client.guilds.get(self.source_guild_id)

    async def fetch(self):
        data = await rest.get_template.request(
            self.state.client.rest, {'template_code': self.code}
        )

        return self.update(data)

    async def create_guild(self, *, name, icon=None):
        json = {'name': str(name)}

        if icon is not None:
            json['icon'] = await resolve_image_data(icon)

        data = await rest.create_guild_from_template.request(
            self.state.client.rest, {'template_code': self.code}, json=json
        )

        return self.state.upsert(data)

    async def sync(self):
        data = await rest.sync_guild_template.request(
            self.state.client.rest,
            {'guild_id': self.source_guild_id, 'template_code': self.code}
        )

        return self.update(data)

    async def modify(self, *, name=None, description=undefined):
        json = {}

        if name is not None:
            json['name'] = str(name)

        if description is not undefined:
            if description is not None:
                json['description'] = str(description)
            else:
                json['description'] = None

        data = await rest.modify_guild_template.request(
            self.state.client.rest,
            {'guild_id': self.source_guild_id, 'template_code': self.code},
            json=json
        )

        return self.update(data)

    async def delete(self):
        await rest.delete_guild_template.request(
            self.state.client.rest,
            {'guild_id': self.source_guild_id, 'template_code': self.code}
        )

    def update(self, data):
        super().update(data)

        if 'creator' in data:
            self.state.client.users.upsert(data['creator'])

        return self
