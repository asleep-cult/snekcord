from .basestate import BaseState
from .. import rest
from ..clients.client import ClientClasses
from ..utils import _validate_keys
from ..utils.snowflake import Snowflake

__all__ = ('GuildState', 'GuildBanState')


class GuildState(BaseState):
    def upsert(self, data):
        guild = self.get(Snowflake(data['id']))

        if guild is not None:
            guild.update(data)
        else:
            guild = ClientClasses.Guild.unmarshal(data, state=self)
            guild.cache()

        return guild

    def new_template(self, data):
        return ClientClasses.GuildTemplate.unmarshal(data, state=self)

    def new_template_many(self, values):
        return {self.new_template(value) for value in values}

    async def fetch(self, guild, *, with_counts=None, sync=True):
        params = {}

        if with_counts is not None:
            params['with_counts'] = with_counts

        guild_id = Snowflake.try_snowflake(guild)

        data = await rest.get_guild.request(
            session=self.client.rest,
            fmt=dict(guild_id=guild_id),
            params=params)

        guild = self.upsert(data)

        if sync:
            await guild.sync(data)

        return guild

    async def fetch_many(self, *, before=None, after=None, limit=None):
        params = {}

        if before is not None:
            params['before'] = Snowflake.try_snowflake(before)

        if after is not None:
            params['after'] = Snowflake.try_snowflake(after)

        if limit is not None:
            params['limit'] = int(limit)

        data = await rest.get_user_client_guilds.request(
            session=self.client.rest,
            params=params)

        return self.upsert_all(data)

    async def fetch_preview(self, guild):
        guild_id = Snowflake.try_snowflake(guild)

        data = await rest.get_guild_preview.request(
            session=self.client.rest,
            fmt=dict(guild_id=guild_id))

        return self.upsert(data)

    async def fetch_template(self, code):
        data = await rest.get_template.request(
            session=self.client.rest,
            fmt=dict(code=code))

        return self.new_template(data)

    async def create(self, **kwargs):
        _validate_keys(f'{self.__class__.__name__}.create',
                       kwargs, ('name',), rest.create_guild.json)

        data = await rest.create_guild.request(
            session=self.client.rest, json=kwargs)

        return self.upsert(data)


class GuildBanState(BaseState):
    __key_transformer__ = Snowflake.try_snowflake

    def __init__(self, *, client, guild):
        super().__init__(client=client)
        self.guild = guild

    def upsert(self, data):
        ban = self.get(data['user']['id'])
        if ban is not None:
            ban.update(data)
        else:
            ban = ClientClasses.GuildBan.unmarshal(data, state=self)
            ban.cache()

        return ban

    async def fetch(self, user):
        user_id = Snowflake.try_snowflake(user)

        data = await rest.get_guild_ban.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id, user_id=user_id))

        return self.upsert(data)

    async def fetch_all(self):
        data = await rest.get_guild_bans.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id))

        return self.upsert_all(data)

    async def add(self, user, **kwargs):
        _validate_keys(f'{self.__class__.__name__}.add',
                       kwargs, (), rest.create_guild_ban.json)

        user_id = Snowflake.try_snowflake(user)

        await rest.create_guild_ban.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id, user_id=user_id),
            json=kwargs)

    async def remove(self, user):
        user_id = Snowflake.try_snowflake(user)

        await rest.remove_guild_ban.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id, user_id=user_id))
