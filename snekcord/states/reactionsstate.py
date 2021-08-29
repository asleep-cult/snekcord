from .basestate import BaseState
from .. import http
from ..objects.reactionsobject import Reactions

__all__ = ('ReactionsState',)


class ReactionsState(BaseState):
    def __init__(self, *, client, message):
        super().__init__(client=client)
        self.message = message

    def upsert(self, data):
        ident = self.client.emojis.upsert(data['emoji']).id
        reactions = self.get(ident)

        if reactions is not None:
            reactions.update(data)
        else:
            reactions = Reactions.unmarshal(data, state=self)
            reactions.cache()

        return reactions

    async def add(self, emoji):
        emoji = self.client.emojis.resolve(emoji)

        await http.add_reaction.request(
            self.client.http, channel_id=self.message.channel.id, message_id=self.message.id,
            emoji=emoji.to_reaction()
        )

    async def remove_all(self):
        await http.remove_all_reactions.request(
            self.client.http, channel_id=self.message.channel.id, message_id=self.message.id
        )
