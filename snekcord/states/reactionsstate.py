from .basestate import BaseState
from .. import rest
from ..clients.client import ClientClasses
from ..objects.emojiobject import _resolve_emoji

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
            reactions = ClientClasses.Reactions.unmarshal(data, state=self)
            reactions.cache()

        return reactions

    async def add(self, emoji):
        emoji = _resolve_emoji(self.message.guild.emojis, emoji)

        await rest.add_reaction.request(
            self.client.rest,
            {
                'channel_id': self.message.channel.id,
                'message_id': self.message.id,
                'emoji': emoji.to_reaction()
            }
        )

    async def remove_all(self):
        await rest.remove_all_reactions.request(
            self.client.rest,
            {'channel_id': self.message.channel.id, 'message_id': self.message.id}
        )
