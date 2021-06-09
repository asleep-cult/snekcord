from __future__ import annotations

import typing as t

from .basestate import BaseState
from .. import rest
from ..objects.emojiobject import BUILTIN_EMOJIS, BuiltinEmoji, GuildEmoji
from ..utils import Snowflake

__all__ = ('GuildEmojiState',)

if t.TYPE_CHECKING:
    from ..clients import Client
    from ..objects import Guild
    from ..typing import Json, SnowflakeType


class GuildEmojiState(BaseState[Snowflake, GuildEmoji]):
    __key_transformer__ = Snowflake.try_snowflake
    __guild_emoji_class__ = GuildEmoji

    def __init__(self, *, client: Client, guild: Guild) -> None:
        super().__init__(client=client)
        self.guild = guild

    def upsert(  # type: ignore
        self, data: Json
    ) -> t.Union[GuildEmoji, BuiltinEmoji, None]:
        emoji: t.Union[GuildEmoji, BuiltinEmoji, None]

        emoji_id = data['id']
        if emoji_id is not None:
            emoji = self.get(emoji_id)
            if emoji is not None:
                emoji.update(data)
            else:
                emoji = self.__guild_emoji_class__.unmarshal(
                    data, state=self, guild=self.guild)
                emoji.cache()
        else:
            surrogates = data['name'].encode()
            emoji = BUILTIN_EMOJIS.get(surrogates)

        return emoji

    async def fetch(self, emoji: SnowflakeType) -> GuildEmoji:  # type: ignore
        emoji_id = Snowflake.try_snowflake(emoji)

        data = await rest.get_guild_emoji.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id, emoji_id=emoji_id))

        return self.upsert(data)  # type: ignore

    async def fetch_all(self) -> t.Set[GuildEmoji]:
        data = await rest.get_guild_emojis.request(
            session=self.client.rest,
            fmt=dict(guild_id=self.guild.id))

        return self.upsert_many(data)
