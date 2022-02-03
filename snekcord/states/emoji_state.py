from __future__ import annotations

import typing

from .base_state import (
    CachedEventState,
    CachedStateView,
)
from ..objects import (
    CachedCustomEmoji,
    CustomEmoji,
    SnowflakeWrapper,
)
from ..snowflake import Snowflake
from ..undefined import undefined

if typing.TYPE_CHECKING:
    from .guild_state import SupportsGuildID
    from ..json import JSONObject

__all__ = (
    'SupportsEmojiID',
    'EmojiIDWrapper',
    'EmojiState',
    'GuildEmojisView',
)

SupportsEmojiID = typing.Union[Snowflake, str, int, CustomEmoji]
EmojiIDWrapper = SnowflakeWrapper[SupportsEmojiID, CustomEmoji]


class EmojiState(CachedEventState[SupportsEmojiID, Snowflake, CachedCustomEmoji, CustomEmoji]):
    def to_unique(self, object: SupportsEmojiID) -> Snowflake:
        if isinstance(object, Snowflake):
            return object

        elif isinstance(object, (str, int)):
            return Snowflake(object)

        elif isinstance(object, CustomEmoji):
            return object.id

        raise TypeError('Expected Snowflake, str, int, or CustomEmoji')

    async def for_guild(self, guild: SupportsGuildID) -> GuildEmojisView:
        guild_id = self.client.guilds.to_unique(guild)

        emojis = await self.client.guilds.emoji_refstore.get(guild_id)
        return self.client.create_guild_emojis_view(emojis, guild_id)

    async def upsert(self, data: JSONObject) -> CustomEmoji:
        emoji_id = Snowflake.into(data, 'id')
        assert emoji_id is not None

        guild_id = Snowflake.into(data, 'guild_id')
        if guild_id is not None:
            await self.client.guilds.emoji_refstore.add(guild_id, emoji_id)

        user = data.get('user')
        if user is not None:
            data['user_id'] = Snowflake(user['id'])
            await self.client.users.upsert(user)

        async with self.synchronize(emoji_id):
            emoji = await self.cache.get(emoji_id)

            if emoji is None:
                emoji = CachedCustomEmoji.from_json(data)
                await self.cache.create(emoji_id, emoji)
            else:
                emoji.update(data)
                await self.cache.update(emoji_id, emoji)

        return await self.from_cached(emoji)

    async def from_cached(self, cached: CachedCustomEmoji) -> CustomEmoji:
        user_id = undefined.nullify(cached.user_id)

        return CustomEmoji(
            state=self,
            id=Snowflake(cached.id),
            guild=SnowflakeWrapper(cached.guild_id, state=self.client.guilds),
            name=cached.name,
            require_colons=cached.require_colons,
            managed=cached.managed,
            animated=cached.animated,
            available=cached.available,
            user=SnowflakeWrapper(user_id, state=self.client.users),
            # roles=self.client.create_emoji_roles_view(cached.role_ids),
        )

    async def remove_refs(self, object: CachedCustomEmoji) -> None:
        if object.guild_id is not None:
            await self.client.guilds.emoji_refstore.remove(object.guild_id, object.id)


class GuildEmojisView(CachedStateView[SupportsEmojiID, Snowflake, CustomEmoji]):
    def __init__(
        self, *, state: EmojiState, emojis: typing.Iterable[SupportsEmojiID], guild: SupportsGuildID
    ) -> None:
        super().__init__(state=state, keys=emojis)
        self.guild_id = self.client.guilds.to_unique(guild)
