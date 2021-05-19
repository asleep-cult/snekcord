from .basestate import BaseState
from .. import rest
from ..objects.reactionobject import Reaction

__all__ = ('ReactionState',)


class ReactionState(BaseState):
    __reaction_class__ = Reaction

    def __init__(self, *, manager, message):
        super().__init__(manager=manager)
        self.message = message

    @property
    def channel(self):
        return self.message.channel

    async def delete_all(self):
        await rest.delete_all_reactions.request(
            session=self.manager.rest,
            fmt=dict(channel_id=self.channel.id,
                     message_id=self.message.id))

    def append(self, data):
        ident = self.guild.emojis.append(data['emoji']).id
        reaction = self.get(ident)
        if reaction is not None:
            reaction.update(data)
        else:
            reaction = self.__reaction_class__.unmarshal(data, state=self)
            reaction.cache()

        return reaction
