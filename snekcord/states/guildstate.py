from __future__ import annotations

import typing as t

from .basestate import BaseState
from .. import rest
from ..objects.guildobject import Guild, GuildBan
from ..objects.templateobject import GuildTemplate
from ..utils import Snowflake, _validate_keys

__all__ = ('GuildState',)

if t.TYPE_CHECKING:
    from ..clients import Client
    from ..typing import IntConvertable, Json, SnowflakeType


class GuildState(BaseState[Snowflake, Guild]):
    __key_transformer__ = Snowflake.try_snowflake
    __guild_class__ = Guild
    __guild_template_class__ = GuildTemplate

    def upsert(self, data: Json) -> Guild:  # type: ignore
        guild = self.get(data['id'])
        if guild is not None:
            guild.update(data)
        else:
            guild = self.__guild_class__.unmarshal(data, state=self)
            guild.cache()

        return guild

    def new_template(self, data: Json) -> GuildTemplate:
        return self.__guild_template_class__.unmarshal(data, state=self)

    def new_template_many(
        self, values: t.Iterable[Json]
    ) -> t.List[GuildTemplate]:
        return [self.new_template(value) for value in values]

    async def fetch(  # type: ignore
        self, guild: SnowflakeType, *,
        with_counts: t.Optional[bool] = None, sync: bool = True
    ) -> Guild:
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

    async def fetch_many(
        self, *, before: t.Optional[SnowflakeType] = None,
        after: t.Optional[SnowflakeType] = None,
        limit: t.Optional[IntConvertable] = None
    ) -> t.Set[Guild]:
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

        return self.upsert_many(data)

    async def fetch_preview(self, guild: SnowflakeType) -> Guild:
        guild_id = Snowflake.try_snowflake(guild)

        data = await rest.get_guild_preview.request(
            session=self.client.rest,
            fmt=dict(guild_id=guild_id))

        return self.upsert(data)

    async def fetch_template(self, code: str) -> GuildTemplate:
        data = await rest.get_template.request(
            session=self.client.rest,
            fmt=dict(code=code))

        return self.new_template(data)

    async def create(self, **kwargs: t.Any) -> Guild:
        _validate_keys(f'{self.__class__.__name__}.create',  # type: ignore
                       kwargs, ('name',), rest.create_guild.json)

        data = await rest.create_guild.request(
            session=self.client.rest, json=kwargs)

        return self.upsert(data)


class GuildBanState(BaseState[Snowflake, GuildBan]):
    __key_transformer__ = Snowflake.try_snowflake
    __ban_class__ = GuildBan

    def __init__(self, *, client: Client, guild: Guild) -> None:
        super().__init__(client=client)
        self.guild = guild

    def upsert(self, data: Json) -> GuildBan:
        ban = self.get(data['user']['id'])
        if ban is not None:
            ban.update(data)
        else:
            ban = self.__ban_class__.unmarshal(
                data, state=self, guild=self.guild)
            ban.cache()

        return ban

    async def fetch(self, user: SnowflakeType) -> GuildBan:  # type: ignore
        user_id = Snowflake.try_snowflake(user)

        data = await rest.get_guild_ban.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id, user_id=user_id))

        return self.upsert(data)

    async def fetch_all(self) -> t.Set[GuildBan]:
        data = await rest.get_guild_bans.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id))

        return self.upsert_many(data)

    async def add(self, user: SnowflakeType, **kwargs: t.Any) -> None:
        _validate_keys(f'{self.__class__.__name__}.add',  # type: ignore
                       kwargs, (), rest.create_guild_ban.json)

        user_id = Snowflake.try_snowflake(user)

        await rest.create_guild_ban.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id, user_id=user_id),
            json=kwargs)

    async def remove(self, user: SnowflakeType) -> None:
        user_id = Snowflake.try_snowflake(user)

        await rest.remove_guild_ban.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id, user_id=user_id))
