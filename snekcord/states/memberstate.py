from __future__ import annotations

import typing as t

from .basestate import BaseState
from .. import rest
from ..objects.memberobject import GuildMember
from ..utils import Snowflake, _validate_keys

__all__ = ('GuildMemberState',)

if t.TYPE_CHECKING:
    from ..clients import Client
    from ..objects import Guild
    from ..typing import Json, IntConvertable, SnowflakeType


class GuildMemberState(BaseState[Snowflake, GuildMember]):
    __key_transformer__ = Snowflake.try_snowflake
    __guild_member_class__ = GuildMember

    if t.TYPE_CHECKING:
        guild: Guild

    def __init__(self, *, client: Client, guild: Guild) -> None:
        super().__init__(client=client)
        self.guild = guild

    def upsert(self, data: Json) -> GuildMember:  # type: ignore
        member = self.get(data['user']['id'])
        if member is not None:
            member.update(data)
        else:
            member = self.__guild_member_class__.unmarshal(
                data, state=self)
            member.cache()

        return member

    async def fetch(self, user: SnowflakeType) -> GuildMember:  # type: ignore
        user_id = Snowflake.try_snowflake(user)

        data = await rest.get_guild_member.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id,
                     user_id=user_id))

        return self.upsert(data)

    async def fetch_many(
        self, *,
        before: t.Optional[SnowflakeType] = None,
        after: t.Optional[SnowflakeType] = None,
        limit: t.Optional[IntConvertable] = None
    ) -> t.Set[GuildMember]:
        params: Json = {}

        if before is not None:
            params['before'] = Snowflake.try_snowflake(before)

        if after is not None:
            params['after'] = Snowflake.try_snowflake(after)

        if limit is not None:
            params['limit'] = int(limit)

        data = await rest.get_guild_members.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id),
            params=params)

        return self.upsert_many(data)

    async def search(
        self, query: str, limit: t.Optional[IntConvertable] = None
    ) -> t.Set[GuildMember]:
        params: Json = {'query': query}

        if limit is not None:
            params['limit'] = int(limit)

        data = await rest.search_guild_members.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id),
            params=params)

        return self.upsert_many(data)

    async def add(
        self, user: SnowflakeType, **kwargs: t.Any
    ) -> None:
        _validate_keys(f'{self.__class__.__name__}.add',  # type: ignore
                       kwargs, ('access_token',), rest.add_guild_member.json)

        user_id = Snowflake.try_snowflake(user)

        await rest.add_guild_member.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id, user_id=user_id),
            json=kwargs)

    async def remove(self, user: SnowflakeType) -> None:
        user_id = Snowflake.try_snowflake(user)

        await rest.remove_guild_member.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id, user_id=user_id))
