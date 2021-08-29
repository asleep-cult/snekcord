from .basestate import BaseState
from .. import http
from ..objects.memberobject import GuildMember
from ..snowflake import Snowflake

__all__ = ('GuildMemberState',)


class GuildMemberState(BaseState):
    def __init__(self, *, client, guild):
        super().__init__(client=client)
        self.guild = guild

    def upsert(self, data):
        member = self.get(Snowflake(data['user']['id']))

        if member is not None:
            member.update(data)
        else:
            member = GuildMember.unmarshal(data, state=self)
            member.cache()

        return member

    async def fetch(self, user):
        user_id = Snowflake.try_snowflake(user)

        data = await http.get_guild_member.request(
            self.client.http, guild_id=self.guild.id, user_id=user_id
        )

        return self.upsert(data)

    async def fetch_many(self, *, after=None, limit=None):
        params = {}

        if after is not None:
            params['after'] = Snowflake.try_snowflake(after, allow_datetime=True)

        if limit is not None:
            params['limit'] = int(limit)

        data = await http.get_guild_members.request(
            self.client.http, guild_id=self.guild.id, params=params
        )

        return [self.upsert(member) for member in data]

    async def search(self, query, *, limit=None):
        params = {}

        params['query'] = str(query)

        if limit is not None:
            params['limit'] = int(limit)

        data = await http.search_guild_members.request(
            self.client.http, guild_id=self.guild.id, params=params
        )

        return [self.upsert(member) for member in data]

    async def add(self, user, access_token, *, nick=None, roles=None, mute=None, deaf=None):
        json = {'access_token': str(access_token)}

        if nick is not None:
            json['nick'] = str(nick)

        if roles is not None:
            json['roles'] = Snowflake.try_snowflake_many(roles)

        if mute is not None:
            json['mute'] = bool(mute)

        if deaf is not None:
            json['deaf'] = bool(deaf)

        user_id = Snowflake.try_snowflake(user)

        await http.add_guild_member.request(
            self.client.http, guild_id=self.guild.id, user_id=user_id, json=json
        )

    async def remove(self, user):
        user_id = Snowflake.try_snowflake(user)

        await http.remove_guild_member.request(
            self.client.http, guild_id=self.guild.id, user_id=user_id
        )
