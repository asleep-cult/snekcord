from __future__ import annotations

import typing

from ..cache import RefStore, SnowflakeMemoryRefStore
from ..enums import CacheFlags
from ..json import JSONObject, json_get
from ..objects import (
    CachedCustomEmoji,
    CustomEmoji,
    EmojiIDWrapper,
    SupportsEmojiID,
    SupportsGuildID,
)
from ..snowflake import Snowflake
from ..undefined import undefined
from .base_state import CachedEventState, CachedStateView

if typing.TYPE_CHECKING:
    from ..clients import Client

__all__ = ('EmojiState', 'GuildEmojisView')


class EmojiState(CachedEventState[SupportsEmojiID, Snowflake, CachedCustomEmoji, CustomEmoji]):
    def __init__(self, *, client: Client) -> None:
        super().__init__(client=client)
        self.guild_refstore = self.create_guild_refstore()

    def create_guild_refstore(self) -> RefStore[Snowflake, Snowflake]:
        return SnowflakeMemoryRefStore()

    def to_unique(self, object: SupportsEmojiID) -> Snowflake:
        if isinstance(object, Snowflake):
            return object

        elif isinstance(object, (str, int)):
            return Snowflake(object)

        elif isinstance(object, CustomEmoji):
            return object.id

        raise TypeError('Expected Snowflake, str, int, or CustomEmoji')

    def wrap(self, emoji: typing.Optional[SupportsEmojiID]) -> EmojiIDWrapper:
        if emoji is not None:
            emoji = self.to_unique(emoji)

        return EmojiIDWrapper(state=self, id=emoji)

    async def for_guild(self, guild: SupportsGuildID) -> GuildEmojisView:
        guild_id = self.client.guilds.to_unique(guild)

        emojis = await self.guild_refstore.get(guild_id)
        return self.client.create_guild_emojis_view(emojis, guild_id)

    async def upsert_cached(
        self, data: JSONObject, flags: CacheFlags = CacheFlags.ALL
    ) -> CachedCustomEmoji:
        emoji_id = Snowflake.into(data, 'id')
        assert emoji_id is not None

        guild_id = Snowflake.into(data, 'guild_id')
        if guild_id is not None and flags & CacheFlags.GUILDS:
            await self.guild_refstore.add(guild_id, emoji_id)

        user = json_get(data, 'user', JSONObject, default=None)
        if user is not None:
            data['user_id'] = Snowflake(json_get(user, 'id', str))

            if flags & CacheFlags.USERS:
                await self.client.users.upsert_cached(user, flags)

        async with self.synchronize(emoji_id):
            cached = await self.cache.get(emoji_id)

            if cached is None:
                cached = CachedCustomEmoji.from_json(data)

                if flags & CacheFlags.EMOJIS:
                    await self.cache.create(emoji_id, cached)
            else:
                cached.update(data)
                await self.cache.update(emoji_id, cached)

        return cached

    async def from_cached(self, cached: CachedCustomEmoji) -> CustomEmoji:
        user_id = undefined.nullify(cached.user_id)

        return CustomEmoji(
            client=self.client,
            id=Snowflake(cached.id),
            guild=self.client.guilds.wrap(cached.guild_id),
            name=cached.name,
            require_colons=cached.require_colons,
            managed=cached.managed,
            animated=cached.animated,
            available=cached.available,
            user=self.client.users.wrap(user_id),
            # roles=self.client.create_emoji_roles_view(cached.role_ids),
        )

    async def remove_refs(self, object: CachedCustomEmoji) -> None:
        if object.guild_id is not None:
            await self.guild_refstore.remove(object.guild_id, object.id)


class GuildEmojisView(CachedStateView[SupportsEmojiID, Snowflake, CustomEmoji]):
    def __init__(
        self, *, state: EmojiState, emojis: typing.Iterable[SupportsEmojiID], guild: SupportsGuildID
    ) -> None:
        super().__init__(state=state, keys=emojis)
        self.guild_id = self.client.guilds.to_unique(guild)
