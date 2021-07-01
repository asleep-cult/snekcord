from .basestate import BaseState
from .. import rest
from ..clients.client import ClientClasses
from ..utils import _validate_keys
from ..utils.snowflake import Snowflake

__all__ = ('GuildMemberState',)


class GuildMemberState(BaseState):
    __key_transformer__ = Snowflake.try_snowflake

    def __init__(self, *, client, guild):
        super().__init__(client=client)
        self.guild = guild

    def upsert(self, data):
        member = self.get(Snowflake(data['user']['id']))

        if member is not None:
            member.update(data)
        else:
            member = ClientClasses.GuildMember.unmarshal(data, state=self)
            member.cache()

        return member

    async def fetch(self, user):
        user_id = Snowflake.try_snowflake(user)

        data = await rest.get_guild_member.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id,
                     user_id=user_id))

        return self.upsert(data)

    async def fetch_many(self, *, before=None, after=None, limit=None):
        params = {}

        if before is not None:
            params['before'] = Snowflake.try_snowflake(before)

        if after is not None:
            params['after'] = Snowflake.try_snowflake(after)

        if limit is not None:
            params['limit'] = limit

        data = await rest.get_guild_members.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id),
            params=params)

        members = []

        for member in data:
            members.append(self.upsert(member))

        return members

    async def search(self, query, limit=None):
        params = {'query': query}

        if limit is not None:
            params['limit'] = limit

        data = await rest.search_guild_members.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id),
            params=params)

        members = []

        for member in data:
            members.append(self.upsert(member))

        return members

    async def add(self, user, **kwargs):
        _validate_keys(f'{self.__class__.__name__}.add',
                       kwargs, ('access_token',), rest.add_guild_member.json)

        user_id = Snowflake.try_snowflake(user)

        await rest.add_guild_member.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id, user_id=user_id),
            json=kwargs)

    async def remove(self, user):
        user_id = Snowflake.try_snowflake(user)

        await rest.remove_guild_member.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id, user_id=user_id))
