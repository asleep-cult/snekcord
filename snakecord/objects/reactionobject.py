from .baseobject import BaseObject
from .. import rest
from ..utils import JsonField, JsonTemplate

__all__ = ('Reaction',)


ReactionTemplate = JsonTemplate(
    count=JsonField('count'),
    me=JsonField('me'),
)


class Reaction(BaseObject, template=ReactionTemplate):
    __slots__ = ('emoji', 'reactors')

    def __json_init__(self, *, state):
        super().__json_init__(state=state)
        self.emoji = None
        self.reactors = self.state.manager.get_class('ReactorState')(
            superstate=self.state.manager.users, reaction=self)

    @property
    def channel(self):
        return self.state.channel

    @property
    def message(self):
        return self.state.message

    async def delete(self):
        await rest.delete_reactions.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.state.channel.id,
                     message_id=self.state.message.id,
                     emoji=self.emoji.to_reaction()))

    def update(self, data, *args, **kwargs):
        super().update(*args, **kwargs)

        emoji = data.get('emoji')
        if emoji is not None:
            self.emoji = self.state.guild.emojis.append(emoji)
            self.id = self.emoji.id
