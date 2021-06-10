from __future__ import annotations

import typing as t

from .basestate import BaseState
from .. import rest
from ..utils import Snowflake

__all__ = ('ReactionsState',)

if t.TYPE_CHECKING:
    from ..clients import Client
    from ..objects import BuiltinEmoji, GuildEmoji, Message, Reactions
    from ..typing import Json


class ReactionsState(BaseState[Snowflake, 'Reactions']):

    def __init__(self, *, client: Client, message: Message) -> None:
        super().__init__(client=client)
        self.message = message

    def upsert(self, data: Json) -> Reactions:  # type: ignore
        ident = (
            self.message.guild.emojis.upsert(data['emoji']).id  # type: ignore
        )
        reactions: t.Optional[Reactions]
        reactions = self.get(ident)
        if reactions is not None:
            reactions.update(data)
        else:
            from ..objects import Reactions  # Prevent circular imports

            reactions = Reactions.unmarshal(data, state=self)
            reactions.cache()

        return reactions

    async def add(
        self, emoji: t.Union[GuildEmoji, BuiltinEmoji]
    ) -> None:
        await rest.create_reaction.request(
            session=self.client.rest,
            fmt=dict(channel_id=self.message.channel_id,
                     message_id=self.message.id,
                     emoji=emoji.to_reaction()))

    async def remove_all(self):
        await rest.delete_all_reactions.request(
            session=self.client.rest,
            fmt=dict(channel_id=self.message.channel_id,
                     message_id=self.message.id))
