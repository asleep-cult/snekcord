from .basestate import BaseState
from .. import rest
from ..objects.guildobject import Guild, GuildBan
from ..objects.templateobject import GuildTemplate
from ..utils import Snowflake, _validate_keys

__all__ = ('GuildState',)


class GuildState(BaseState):
    __key_transformer__ = Snowflake.try_snowflake
    __guild_class__ = Guild
    __guild_template_class__ = GuildTemplate

    async def new(self, data):
        guild = await self.get(data['id'])
        if guild is not None:
            await guild.update(data)
        else:
            guild = await self.__guild_class__.unmarshal(data, state=self)
            await guild.cache()

        return guild

    async def new_template(self, data):
        return await self.__guild_template_class__.unmarshal(data, state=self)

    async def create(self, **kwargs):
        required_keys = ('name',)
        keys = rest.create_guild.json

        _validate_keys(f'{self.__class__.__name__}.create',
                       kwargs, required_keys, keys)

        data = await rest.create_guild.request(
            session=self.manager.rest, json=kwargs)

        return await self.new(data)

    async def fetch(self, guild):
        guild_id = Snowflake.try_snowflake(guild)

        data = await rest.get_guild.request(
            session=self.manager.rest,
            fmt=dict(guild_id=guild_id))

        return await self.new(data)

    async def bulk_fetch(self, *, before=None, after=None, limit=None):
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

        return await self.new(data)

    async def fetch_preview(self, guild):
        guild_id = Snowflake.try_snowflake(guild)

        data = await rest.get_guild_preview.request(
            state=self.manager.state,
            fmt=dict(guild_id=guild_id))

        return await self.new(data)

    async def fetch_template(self, code):
        data = await rest.get_template.request(
            session=self.manager.rest,
            fmt=dict(code=code))

        return await self.new_template(data)


class GuildBanState(BaseState):
    __key_transformer__ = Snowflake.try_snowflake
    __maxsize__ = -1
    __ban_class__ = GuildBan

    def __init__(self, *, manager, guild):
        super().__init__(manager=manager)
        self.guild = guild

    async def fetch(self, user):
        user_id = Snowflake.try_snowflake(user)

        data = await rest.get_guild_ban.request(
            session=self.manager.rest,
            fmt=dict(guild_id=self.guild.id, user_id=user_id))

        return await self.new(data)

    async def fetch_all(self):
        data = await rest.get_guild_bans.request(
            session=self.manager.rest,
            fmt=dict(guild_id=self.guild.id))

        return await self.new(data)

    async def add(self, user, **kwargs):
        keys = rest.create_guild_ban.json

        _validate_keys(f'{self.__class__.__name__}.create',
                       kwargs, (), keys)

        user_id = Snowflake.try_snowflake(user)

        data = await rest.create_guild_ban.request(
            session=self.state.manager.rest,
            fmt=dict(guild_id=self.guild.id, user_id=user_id),
            json=kwargs)

        return await self.new(data)

    async def remove(self, user):
        user_id = Snowflake.try_snowflake(user)

        await rest.remove_guild_ban.request(
            session=self.manager.rest,
            fmt=dict(guild_id=self.guild.id, user_id=user_id))
