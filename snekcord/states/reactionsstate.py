from .basestate import BaseState
from .. import rest
from ..objects import Reactions

__all__ = ('ReactionsState',)


class ReactionsState(BaseState):

    def __init__(self, *, client, message):
        super().__init__(client=client)
        self.message = message

    def upsert(self, data):
        ident = self.message.guild.emojis.upsert(data['emoji']).id
        reactions = self.get(ident)
        if reactions is not None:
            reactions.update(data)
        else:
            reactions = Reactions.unmarshal(data, state=self)
            reactions.cache()

        return reactions

    async def add(self, emoji):
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
