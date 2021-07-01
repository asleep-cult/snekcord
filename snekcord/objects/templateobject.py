from datetime import datetime

from .baseobject import BaseObject
from .. import rest
from ..utils import JsonField, Snowflake, _validate_keys

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
    serialized_source_guild = JsonField('serialized_source_guild')
    # if someone actually needs this field to be more user friendly...
    # ever... make an issue https://github.com/asleep-cult/snekcord/issues
    is_dirty = JsonField('is_dirty')

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
            session=self.state.client.rest,
            fmt=dict(code=self.code))

        self.update(data)

        return self

    async def create_guild(self, **kwargs):
        _validate_keys(f'{self.__class__.__name__}.create_guild',
                       kwargs, ('name',), rest.create_guild_from_template.json)

        data = await rest.create_guild_from_template.request(
            session=self.state.client.rest,
            fmt=dict(template_code=self.code),
            json=kwargs)

        return self.state.client.guilds.upsert(data)

    async def sync(self):
        data = await rest.sync_guild_template.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.source_guild_id,
                     template_code=self.code))

        self.update(data)

        return self

    async def modify(self, **kwargs):
        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), rest.modify_guild_template.json)

        data = await rest.modify_guild_template.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.source_guild_id,
                     template_code=self.code),
            json=kwargs)

        self.update(data)

        return self

    async def delete(self) -> None:
        await rest.delete_guild_template.request(
            session=self.state.client.rest,
            fmt=dict(guild_id=self.source_guild_id,
                     template_code=self.code))

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        creator = data.get('creator')
        if creator is not None:
            self.state.client.users.upsert(creator)
