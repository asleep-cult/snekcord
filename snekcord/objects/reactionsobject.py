from .baseobject import BaseObject
from .. import rest
from ..states.basestate import BaseSubState
from ..utils import JsonField, Snowflake

__all__ = ('Reactions',)


class Reactions(BaseSubState, BaseObject):
    __slots__ = ('emoji',)

    id = JsonField('id')
    count = JsonField('count')
    me = JsonField('me')

    def __init__(self, *, state):
        BaseSubState.__init__(self, superstate=state.client.users)
        BaseObject.__init__(self, state=state)
        self.emoji = None

    def upsert(self, data):
        user = self.superstate.upsert(data)
        self.add_key(user.id)
        return user

    @property
    def message(self):
        return self.state.message

    async def fetch_many(self, after=None, limit=None):
        params = {}

        if after is not None:
            params['after'] = Snowflake.try_snowflake(after, allow_datetime=True)

        if limit is not None:
            params['limit'] = int(limit)

        data = await rest.get_reactions.request(
            self.state.client.rest,
            {
                'channel_id': self.state.message.channel.id,
                'message_id': self.state.message.id,
                'emoji': self.emoji.to_reaction()
            }
        )

        return [self.upsert(user) for user in data]

    async def add(self):
        await self.state.add(self.emoji)

    async def remove(self, user):
        user_id = Snowflake.try_snowflake(user)

        await rest.remove_reaction.request(
            self.state.client.rest,
            {
                'channel_id': self.state.message.channel.id,
                'message_id': self.state.message.id,
                'emoji': self.emoji.to_reaction(),
                'user_id': user_id
            }
        )

    async def remove_me(self):
        await rest.remove_reaction.request(
            self.state.client.rest,
            {
                'channel_id': self.state.message.channel.id,
                'message_id': self.state.message.id,
                'emoji': self.emoji.to_reaction(),
                'user_id': '@me'
            }
        )

    async def remove_all(self):
        await rest.remove_reactions.request(
            self.state.client.rest,
            {
                'channel_id': self.state.message.channel.id,
                'message_id': self.state.message.id,
                'emoji': self.emoji.to_reaction()
            }
        )

    def update(self, data):
        super().update(data)

        if 'emoji' in data:
            self.emoji = self.state.message.guild.emojis.upsert(data['emoji'])
            self._json_data_['id'] = self.emoji.id

        return self
