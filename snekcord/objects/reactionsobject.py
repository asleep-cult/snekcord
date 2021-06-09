from __future__ import annotations

import typing as t

from .baseobject import BaseObject
from .. import rest
from ..states.basestate import BaseSubState
from ..utils import JsonField, JsonTemplate, Snowflake

__all__ = ('Reactions',)

if t.TYPE_CHECKING:
    from .emojiobject import BuiltinEmoji, GuildEmoji
    from .messageobject import Message
    from .userobject import User
    from ..states import ReactionsState, UserState
    from ..typing import IntConvertable, Json, SnowflakeType

ReactionsTemplate = JsonTemplate(
    count=JsonField('count'),
    me=JsonField('me'),
)


class Reactions(
    BaseSubState[Snowflake, User], BaseObject, template=ReactionsTemplate
):
    __slots__ = ('emoji',)

    if t.TYPE_CHECKING:
        id: t.Union[bytes, Snowflake]
        state: ReactionsState
        superstate: UserState
        emoji: t.Optional[t.Union[BuiltinEmoji, GuildEmoji]]

    def __init__(self, *, state: ReactionsState) -> None:
        BaseSubState.__init__(  # type: ignore
            self, superstate=state.client.users)
        BaseObject.__init__(self, state=state)
        self.emoji = None

    @property
    def message(self) -> Message:
        return self.state.message

    async def fetch_many(
        self,
        after: t.Optional[SnowflakeType] = None,
        limit: t.Optional[IntConvertable] = None
    ) -> t.Set[User]:
        params: Json = {}

        if after is not None:
            params['after'] = Snowflake.try_snowflake(after)

        if limit is not None:
            params['limit'] = int(limit)

        assert self.emoji is not None

        data = await rest.get_reactions.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.state.message.channel_id,
                     message_id=self.state.message.id,
                     emoji=self.emoji.to_reaction()))

        users = self.superstate.upsert_many(data)
        self.extend_keys(user.id for user in users)

        return users

    async def add(self) -> None:
        assert self.emoji is not None
        await self.state.add(self.emoji)

    async def remove(
        self, user: t.Optional[SnowflakeType] = None
    ) -> None:
        if user is not None:
            user_id = Snowflake.try_snowflake(user)
        else:
            user_id = '@me'

        assert self.emoji is not None

        await rest.delete_reaction.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.state.message.channel_id,
                     message_id=self.state.message.id,
                     emoji=self.emoji.to_reaction(),
                     user_id=user_id))

    async def remove_all(self):
        assert self.emoji is not None
        await rest.delete_reactions.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.state.message.channel_id,
                     message_id=self.state.message.id,
                     emoji=self.emoji.to_reaction()))

    def update(  # type: ignore
        self, data: Json,
        *args: t.Any, **kwargs: t.Any
    ) -> None:
        super().update(data, *args, **kwargs)

        emoji = data.get('emoji')
        if emoji is not None:
            self.emoji = (
                self.state.message.guild.emojis.upsert(  # type: ignore
                    emoji)
            )
            self.id = self.emoji.id  # type: ignore
