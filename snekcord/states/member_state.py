from __future__ import annotations

import typing
from datetime import datetime

from ..cache import RefStore, SnowflakeMemoryRefStore
from ..enums import CacheFlags
from ..json import JSONObject, JSONType, json_get
from ..objects import (
    CachedMember,
    Member,
    SnowflakeWrapper,
    SupportsGuildID,
    SupportsMemberID,
    SupportsUserID,
)
from ..snowflake import Snowflake, SnowflakeCouple
from ..undefined import undefined
from .base_state import CachedEventState, CachedState

if typing.TYPE_CHECKING:
    from ..clients import Client

__all__ = ('MemberState', 'GuildMembersView')


class MemberState(CachedEventState[SupportsMemberID, SnowflakeCouple, CachedMember, Member]):
    def __init__(self, *, client: Client) -> None:
        super().__init__(client=client)
        self.guild_refstore = self.create_guild_refstore()

    def create_guild_refstore(self) -> RefStore[Snowflake, Snowflake]:
        return SnowflakeMemoryRefStore()

    def to_unique(self, object: SupportsMemberID) -> SnowflakeCouple:
        if isinstance(object, SnowflakeCouple):
            return object

        elif isinstance(object, tuple):
            if len(object) != 2:
                raise TypeError('tuple should have 2 items')

            guild_id = self.client.guilds.to_unique(object[0])
            user_id = self.client.users.to_unique(object[1])

            return SnowflakeCouple(guild_id, user_id)

        elif isinstance(object, Member):
            return object.id

        raise TypeError('Expected SnowflakeCouple, tuple, or Member')

    async def for_guild(self, guild: SupportsGuildID) -> GuildMembersView:
        guild_id = self.client.guilds.to_unique(guild)

        users = await self.guild_refstore.get(guild_id)
        return self.client.create_guild_members_view(users, guild_id)

    def inject_metadata(self, data: JSONType, guild_id: Snowflake) -> JSONObject:
        if not isinstance(data, dict):
            raise TypeError('data should be a JSON object')

        return dict(data, guild_id=guild_id)

    async def upsert_cached(
        self, data: JSONObject, flags: CacheFlags = CacheFlags.ALL
    ) -> CachedMember:
        user = json_get(data, 'user', JSONObject, default=None)
        if user is not None:
            data['user_id'] = Snowflake(json_get(user, 'id', str))

            if flags & CacheFlags.USERS:
                await self.client.users.upsert(user)

        user_id = Snowflake.into(data, 'user_id')
        assert user_id is not None

        guild_id = Snowflake.into(data, 'guild_id')
        assert guild_id is not None

        role_ids = json_get(data, 'roles', typing.List[str], default=())
        data['role_ids'] = [Snowflake(role_id) for role_id in role_ids]

        if flags & CacheFlags.MEMBERS:
            await self.guild_refstore.add(guild_id, user_id)

        member_id = SnowflakeCouple(guild_id, user_id)

        async with self.synchronize(member_id):
            cached = await self.cache.get(member_id)

            if cached is None:
                cached = CachedMember.from_json(data)

                if flags & CacheFlags.MEMBERS:
                    await self.cache.create(member_id, cached)
            else:
                cached.update(data)
                await self.cache.update(member_id, cached)

        return cached

    async def from_cached(self, cached: CachedMember) -> Member:
        premium_since = undefined.nullify(cached.premium_since)
        if premium_since is not None:
            premium_since = datetime.fromisoformat(premium_since)

        return Member(
            client=self.client,
            id=SnowflakeCouple(cached.guild_id, cached.user_id),
            guild=SnowflakeWrapper(cached.guild_id, state=self.client.guilds),
            user=SnowflakeWrapper(cached.user_id, state=self.client.users),
            nick=undefined.nullify(cached.nick),
            avatar=undefined.nullify(cached.avatar),
            joined_at=datetime.fromisoformat(cached.joined_at),
            premium_since=premium_since,
            deaf=cached.deaf,
            mute=cached.mute,
            pending=undefined.nullify(cached.pending),
            communication_disabled_until=undefined.nullify(cached.communication_disabled_until),
        )

    async def remove_refs(self, object: CachedMember) -> None:
        await self.guild_refstore.remove(object.guild_id, object.user_id)


class GuildMembersView(CachedState[SupportsMemberID, SnowflakeCouple, Member]):
    def __init__(
        self,
        *,
        state: MemberState,
        users: typing.Iterable[SupportsUserID],
        guild: SupportsGuildID,
    ) -> None:
        self.state = state
        self.client = self.state.client

        self.user_ids = frozenset(self.client.users.to_unique(user) for user in users)
        self.guild_id = self.client.guilds.to_unique(guild)

    def to_unique(self, object: typing.Union[SupportsUserID, SupportsMemberID]) -> SnowflakeCouple:
        if isinstance(object, SupportsUserID):
            return SnowflakeCouple(self.guild_id, self.client.users.to_unique(object))

        return self.state.to_unique(object)

    def __aiter__(self) -> typing.AsyncIterator[Member]:
        iterator = (
            await self.state.get(SnowflakeCouple(self.guild_id, user_id))
            for user_id in self.user_ids
        )
        return (object async for object in iterator if object is not None)

    async def size(self) -> int:
        return len(self.user_ids)

    async def get(
        self, object: typing.Union[SupportsUserID, SupportsMemberID]
    ) -> typing.Optional[Member]:
        id = self.to_unique(object)
        if id.high != self.guild_id or id.low not in self.user_ids:
            return None

        return await self.state.get(id)
