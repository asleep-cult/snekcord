from .baseobject import BaseObject
from .. import rest
from ..states.basestate import BaseSubState
from ..utils import JsonField, Snowflake

__all__ = ('Reactions',)


class Reactions(BaseSubState, BaseObject):
    __slots__ = ('emoji',)

    id = JsonField('id')
    count = JsonField('count')
    me = JsonField('mw')

    def __init__(self, *, state):
        BaseSubState.__init__(self, superstate=state.client.users)
        BaseObject.__init__(self, state=state)
        self.emoji = None

    @property
    def message(self):
        return self.state.message

    async def fetch_many(self, after=None, limit=None):
        params = {}

        if after is not None:
            params['after'] = Snowflake.try_snowflake(after)

        if limit is not None:
            params['limit'] = limit

        data = await rest.get_reactions.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.state.message.channel_id,
                     message_id=self.state.message.id,
                     emoji=self.emoji.to_reaction()))

        users = []

        for user in data:
            users.append(self.superstate.upsert(user))
            self._keys.add(Snowflake(user['id']))

        return users

    async def add(self):
        await self.state.add(self.emoji)

    async def remove(self, user=None):
        if user is not None:
            user_id = Snowflake.try_snowflake(user)
        else:
            user_id = '@me'

        await rest.delete_reaction.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.state.message.channel_id,
                     message_id=self.state.message.id,
                     emoji=self.emoji.to_reaction(),
                     user_id=user_id))

    async def remove_all(self):
        await rest.delete_reactions.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.state.message.channel_id,
                     message_id=self.state.message.id,
                     emoji=self.emoji.to_reaction()))

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        emoji = data.get('emoji')
        if emoji is not None:
            self.emoji = self.state.message.guild.emojis.upsert(emoji)
            self._json_data_['id'] = self.emoji.id
