from __future__ import annotations

from typing import Union

from .base_state import (
    CachedEventState,
    OnDecoratorT,
)
from ..events import (
    GuildAvailableEvent,
    GuildDeleteEvent,
    GuildEvents,
    GuildJoinEvent,
    GuildReceiveEvent,
    GuildUnavailableEvent,
    GuildUpdateEvent,
)
from ..exceptions import InvalidResponseError
from ..objects import (
    CachedGuild,
    Guild,
    PartialGuild,
    RESTGuild,
    SnowflakeWrapper,
)
from ..rest.endpoints import GET_GUILD
from ..snowflake import Snowflake

SupportsGuildID = Union[Snowflake, str, int, PartialGuild]
GuildIDWrapper = SnowflakeWrapper[SupportsGuildID, Guild]


class GuildState(CachedEventState[SupportsGuildID, Snowflake, CachedGuild, Guild]):
    def to_unique(self, object: SupportsGuildID) -> Snowflake:
        if isinstance(object, Snowflake):
            return object

        elif isinstance(object, (str, int)):
            return Snowflake(object)

        elif isinstance(object, PartialGuild):
            return object.id

        raise TypeError('Expected Snowflake, str, int, or PartialGuild')

    async def upsert(self, data) -> Guild:
        guild_id = Snowflake(data['id'])
        guild = await self.cache.get(guild_id)

        if guild is None:
            guild = CachedGuild.from_json(data)
            await self.cache.create(guild_id, guild)
        else:
            await self.cache.update(guild_id, guild)

        return self.from_cached(guild)

    async def upsert_rest(self, data) -> RESTGuild:
        guild = await self.upsert(data)

        return RESTGuild.from_guild(
            guild,
            presence_count=data.get('approximate_presence_count'),
            member_count=data.get('approximate_member_count'),
        )

    async def fetch(self, guild: SupportsGuildID) -> RESTGuild:
        data = await self.client.rest.request(GET_GUILD, guild_id=self.to_unique(guild))

        if not isinstance(data, dict):
            raise InvalidResponseError(data)

        return await self.upsert(data)

    def on_join(self) -> OnDecoratorT[GuildJoinEvent]:
        return self.on(GuildEvents.JOIN)

    def on_available(self) -> OnDecoratorT[GuildAvailableEvent]:
        return self.on(GuildEvents.AVAILABLE)

    def on_receive(self) -> OnDecoratorT[GuildReceiveEvent]:
        return self.on(GuildEvents.RECEIVE)

    def on_update(self) -> OnDecoratorT[GuildUpdateEvent]:
        return self.on(GuildEvents.UPDATE)

    def on_delete(self) -> OnDecoratorT[GuildDeleteEvent]:
        return self.on(GuildEvents.DELETE)

    def on_unavailable(self) -> OnDecoratorT[GuildUnavailableEvent]:
        return self.on(GuildEvents.UNAVAILABLE)
