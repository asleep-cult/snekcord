from .baseobject import BaseObject
from .. import rest
from ..utils import JsonField, JsonTemplate, Snowflake, _validate_keys

__all__ = ('GuildTemplate',)


GuildTemplateTemplate = JsonTemplate(
    id=JsonField('code'),
    name=JsonField('name'),
    description=JsonField('description'),
    usage_count=JsonField('usage_count'),
    creator_id=JsonField('creator_id', Snowflake, str),
    created_at=JsonField('created_at'),
    updated_at=JsonField('updated_at'),
    source_guild_id=JsonField('source_guild_id', Snowflake, str),
    serialized_source_guild=JsonField('serialized_source_guild'),
    # if someone actually needs this field to be more user friendly...
    # ever... make an issue https://github.com/asleep-cult/snakecord/issues
    is_dirty=JsonField('is_dirty'),
)


class GuildTemplate(BaseObject, template=GuildTemplateTemplate):
    @property
    def code(self):
        return self.id

    async def create_guild(self, **kwargs):
        required_keys = ('name',)
        keys = rest.create_guild_from_template.json

        _validate_keys(f'{self.__class__.__name__}.create_guild',
                       kwargs, required_keys, keys)

        data = await rest.create_guild_from_template.request(
            session=self.state.manager.rest,
            fmt=dict(template_code=self.code),
            json=kwargs)

        return self.state.manager.guilds.append(data)

    async def sync(self):
        data = await rest.sync_guild_template.request(
            session=self.state.manager.rest,
            fmt=dict(guild_id=self.source_guild_id,
                     template_code=self.code))

        self.update(data)

        return self

    async def modify(self, **kwargs):
        keys = rest.modify_guild_template.json

        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), keys)

        data = await rest.modify_guild_template.request(
            sesison=self.state.manager.rest,
            fmt=dict(guild_id=self.source_guild_id,
                     template_code=self.code),
            json=kwargs)

        self.update(data)

        return self

    async def delete(self):
        await rest.delete_guild_template.request(
            session=self.state.manager.rest,
            fmt=dict(guild_id=self.source_guild_id,
                     template_code=self.code))

    async def fetch(self):
        data = await rest.get_template.request(
            session=self.manager.rest,
            fmt=dict(code=self.code))

        self.update(data)

        return self

    async def update(self, data, *args, **kwargs):
        await super().update(data, *args, **kwargs)

        creator = data.get('creator')
        if creator is not None:
            self.state.manager.users.append(creator)
