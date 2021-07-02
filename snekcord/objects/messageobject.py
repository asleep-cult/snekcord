from datetime import datetime

from .baseobject import BaseObject
from .channelobject import GuildChannel
from .embedobject import Embed
from .. import rest
from ..clients.client import ClientClasses
from ..enums import MessageType
from ..flags import MessageFlags
from ..utils import JsonArray, JsonField, Snowflake

__all__ = ('Message',)


class Message(BaseObject):
    __slots__ = ('author', 'member', 'reactions')

    channel_id = JsonField('channel_id', Snowflake)
    guild_id = JsonField('guild_id', Snowflake)
    content = JsonField('content')
    edited_at = JsonField('edited_timestamp', datetime.fromisoformat)
    tts = JsonField('tts')
    mention_everyone = JsonField('mention_everyone')
    _mentions = JsonArray('mentions')
    _mention_roles = JsonArray('mention_roles')
    _mention_channels = JsonArray('mention_channels')
    _attachments = JsonArray('attachments')
    embeds = JsonArray('embeds', object=Embed)
    nonce = JsonField('nonce')
    pinned = JsonField('pinned')
    webhook_id = JsonField('webhook_id', Snowflake)
    type = JsonField('type', MessageType.get_enum)
    _activity = JsonField('activity')
    application = JsonField('application')
    _message_reference = JsonField('message_reference')
    flags = JsonField('flags', MessageFlags.from_value)
    _stickers = JsonArray('stickers')
    _referenced_message = JsonField('referenced_message')
    _interaction = JsonField('interaction')

    def __init__(self, *, state):
        super().__init__(state=state)
        self.author = None
        self.member = None

        self.reactions = ClientClasses.ReactionsState(client=self.state.client, message=self)

    @property
    def channel(self):
        return self.state.channel

    @property
    def guild(self):
        if isinstance(self.channel, GuildChannel):
            return self.channel.guild
        return None

    async def crosspost(self):
        data = await rest.crosspost_message.request(
            self.state.client.rest,
            {'channel_id': self.channel.id, 'message_id': self.id}
        )

        return self.state.upsert(data)

    def delete(self):
        return self.state.delete(self.id)

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        if 'author' in data:
            self.author = self.state.client.users.upsert(data['author'])

            guild = self.guild
            member = data.get('member')
            if member is not None and guild is not None:
                member['user'] = data['author']
                self.member = guild.members.upsert(member)

        if 'reactions' in data:
            reactions = set()

            for reaction in reactions:
                reactions.add(self.reactions.upsert(reaction))

            for emoji_id in set(self.reactions.keys()) - reactions:
                del self.reactions.mapping[emoji_id]
