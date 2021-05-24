from .baseobject import BaseObject, BaseTemplate
from .embedobject import Embed
from .. import rest
from ..utils import JsonArray, JsonField, JsonTemplate, Snowflake

__all__ = ('Message',)


MessageTemplate = JsonTemplate(
    channel_id=JsonField('channel_id', Snowflake, str),
    guild_id=JsonField('guild_id', Snowflake, str),
    content=JsonField('content'),
    edited_timestamp=JsonField('edited_timestamp'),
    tts=JsonField('tts'),
    mention_everyone=JsonField('mention_everyone'),
    _mentions=JsonArray('mentions'),
    _mention_roles=JsonArray('mention_roles'),
    _mention_channels=JsonArray('mention_channels'),
    _attachments=JsonArray('attachments'),
    embeds=JsonArray('embeds', object=Embed),
    nonce=JsonField('nonce'),
    pinned=JsonField('pinned'),
    webhook_id=JsonField('webhook_id'),
    type=JsonField('type'),
    _activity=JsonField('activity'),
    application=JsonField('application'),
    _message_reference=JsonField('message_reference'),
    flags=JsonField('flags'),
    _stickers=JsonArray('stickers'),
    _referenced_message=JsonField('referenced_message'),
    _interaction=JsonField('interaction'),
    __extends__=(BaseTemplate,)
)


class Message(BaseObject, template=MessageTemplate):
    __slots__ = ('author', 'member', 'reactions')

    async def __json_init__(self, *, state):
        await super().__json_init__(state=state)
        self.author = None
        self.member = None
        self.reactions = self.state.manager.get_class('ReactionState')(
            manager=self.state.manager, message=self)

    @property
    def channel(self):
        return self.state.channel

    async def crosspost(self):
        data = await rest.crosspost_message.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.state.channel.id, message_id=self.id))

        return await self.state.new(data)

    async def update(self, data, *args, **kwargs):
        await super().update(data, *args, **kwargs)

        author = data.get('author')
        if author is not None:
            self.author = await self.state.manager.users.new(author)

            guild = self.guild
            member = data.get('member')
            if member is not None and guild is not None:
                member['user'] = author
                self.member = await guild.members.new(member)

        reactions = data.get('reactions')
        if reactions is not None:
            await self.reactions.extend_new(reactions)
