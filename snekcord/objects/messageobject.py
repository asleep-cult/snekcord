from datetime import datetime

from .baseobject import BaseObject
from .embedobject import Embed
from .. import rest
from ..clients.client import ClientClasses
from ..enums import MessageType
from ..flags import MessageFlags
from ..utils.json import JsonArray, JsonField
from ..utils.snowflake import Snowflake

__all__ = ('MessageFlags', 'Message')


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
        return getattr(self.channel, 'guild', None)

    async def crosspost(self):
        data = await rest.crosspost_message.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.channel.id, message_id=self.id))

        return self.state.upsert(data)

    async def delete(self) -> None:
        await rest.delete_message.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.channel.id, message_id=self.id))

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        author = data.get('author')
        if author is not None:
            self.author = self.state.client.users.upsert(author)

            guild = self.guild
            member = data.get('member')
            if member is not None and guild is not None:
                member['user'] = author
                self.member = guild.members.upsert(member)

        reactions = data.get('reactions')
        if reactions is not None:
            self.reactions.clear()
            self.reactions.upsert_many(reactions)
