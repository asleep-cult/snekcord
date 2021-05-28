from .. import rest
from ..objects.reactionobject import Reaction
from ..states.basestate import BaseSubState
from ..utils import Snowflake

__all__ = ('ReactorState',)


class ReactorState(BaseSubState):
    def __init__(self, *, superstate, reaction):
        super().__init__(superstate=superstate)
        self.reaction = reaction

    async def fetch_many(self, *, after=None, limit=None):
        params = {}

        if after is not None:
            params['after'] = after

        if limit is not None:
            params['limit'] = limit

        data = await rest.get_reactions.request(
            session=self.superstate.manager.rest,
            fmt=dict(channel_id=self.reaction.channel.id,
                     message_id=self.reaction.message.id,
                     emoji=self.reaction.emoji.to_reaction()))

        users = self.superstate.manager.users.upsert_many(data)
        self.extend_keys(user.id for user in users)

        return users

    async def delete(self, user=None):
        if user is not None:
            user_id = Snowflake.try_snowflake(user)
        else:
            user_id = '@me'

        await rest.delete_reaction.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.state.channel.id,
                     message_id=self.state.message.id,
                     emoji=self.emoji.to_reaction(),
                     user_id=user_id))
