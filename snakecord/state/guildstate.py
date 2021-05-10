from .basestate import BaseState, SnowflakeMapping, WeakValueSnowflakeMapping
from .. import rest
from ..objects.guildobject import Guild
from ..utils import Snowflake, _validate_keys


class GuildState(BaseState):
    __container__ = SnowflakeMapping
    __recycled_container__ = WeakValueSnowflakeMapping
    __guild_class__ = Guild

    def append(self, data):
        guild = self.get(data['id'])
        if guild is not None:
            guild.update(data)
        else:
            guild = self.__guild_class__.unmarshal(data, state=self)
            guild.cache()

        return guild

    async def create(self, **kwargs):
        required_keys = ('name',)

        keys = rest.create_guild.json

        _validate_keys(f'{self.__class__.__name__}.create',
                       kwargs, required_keys, keys)

        data = await rest.create_guild.request(
            session=self.manager.rest, json=kwargs)

        return self.append(data)

    async def fetch(self, guild_id):
        guild_id = Snowflake.try_snowflake(guild_id)
        data = await rest.get_guild.request(
            session=self.manager.rest,
            fmt=dict(guild_id=guild_id))

        return self.append(data)

    async def fetch_many(self, *, before=None, after=None, limit=None):
        params = {}

        if before is not None:
            params['before'] = Snowflake.try_snowflake(before)

        if after is not None:
            params['after'] = Snowflake.try_snowflake(after)

        if limit is not None:
            params['limit'] = int(limit)

        data = await rest.get_user_client_guilds.request(
            session=self.manager.rest,
            params=params)

        return self.extend(data)

    async def fetch_preview(self, guild_id):
        guild_id = Snowflake.try_snowflake(guild_id)
        data = await rest.get_guild_preview.request(
            state=self.manager.state,
            fmt=dict(guild_id=guild_id))

        return self.append(data)
