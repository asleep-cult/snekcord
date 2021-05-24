from .basestate import BaseState
from .. import rest
from ..objects.memberobject import GuildMember
from ..utils import Snowflake, _validate_keys

__all__ = ('GuildMemberState',)


class GuildMemberState(BaseState):
    __key_transformer__ = Snowflake.try_snowflake
    __guild_member_class__ = GuildMember

    def __init__(self, *, manager, guild):
        super().__init__(manager=manager)
        self.guild = guild

    async def new(self, data):
        member = await self.get(data['id'])
        if member is not None:
            await member.update(data)
        else:
            member = await self.__guild_member_class__.unmarshal(
                data, state=self, guild=self.guild)
            await member.cache()

        return member

    async def fetch(self, user):
        user_id = Snowflake.try_snowflake(user)

        data = await rest.get_guild_member.request(
            session=self.manager.rest,
            fmt=dict(guild_id=self.guild.id,
                     user_id=user_id))

        return await self.new(data)

    async def bulk_fetch(self, *, before=None, after=None, limit=None):
        params = {}

        if before is not None:
            params['before'] = Snowflake.try_snowflake(before)

        if after is not None:
            params['after'] = Snowflake.try_snowflake(after)

        if limit is not None:
            params['limit'] = int(limit)

        data = await rest.get_guild_members.request(
            session=self.manager.rest,
            fmt=dict(guild_id=self.guild.id),
            params=params)

        return await self.extend_new(data)

    async def search(self, query, limit=None):
        params = {'query': query}

        if limit is not None:
            params['limit'] = int(limit)

        data = await rest.search_guild_members.request(
            session=self.manager.rest,
            fmt=dict(guild_id=self.guild.id),
            params=params)

        return await self.extend_new(data)

    async def add(self, user, **kwargs):
        required_keys = ('access_token',)
        keys = rest.add_guild_member.keys

        _validate_keys(f'{self.__class__.__name__}.add',
                       kwargs, required_keys, keys)

        user_id = Snowflake.try_snowflake(user)

        data = await rest.add_guild_member.request(
            session=self.manager.rest,
            fmt=dict(guild_id=self.guild.id, user_id=user_id),
            json=kwargs)

        return await self.new(data)

    async def remove(self, user):
        user_id = Snowflake.try_snowflake(user)

        await rest.remove_guild_member.request(
            session=self.manager.rest,
            fmt=dict(guild_id=self.guild.id, user_id=user_id))
