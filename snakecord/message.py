from . import structures
from .state import BaseState
from .utils import _try_snowflake


class Reaction(structures.Reaction):
    def __init__(self, state, message):
        self._state = state
        self.message = message

    async def remove(self, user=None):
        await self._state.remove(self.emoji, user)

    async def remove_all(self):
        await self._state.remove_emoji(self.emoji)


class Message(structures.Message):
    def __init__(self, *, state, channel):
        self._state = state
        self.channel = channel
        self.reactions = ReactionState(self._state.client, self)

    async def edit(self, content=None, *, embed=None, flags=None, allowed_mentions=None):
        rest = self._state._client.rest

        if embed is not None:
            embed = embed.to_dict()

        data = await rest.edit_message(
            self.channel.id, self.id, content=content,
            embed=embed, flags=flags,
            allowed_mentions=allowed_mentions
        )
        message = self._state._add(data, channel=self.channel)
        return message

    async def crosspost(self):
        rest = self._state._client.rest
        data = await rest.crosspost_message(self.channel.id, self.id)
        message = self._state._add(data, channel=self.channel)
        return message

    async def delete(self):
        rest = self._state._client.rest
        await rest.edit_message(self.channel.id, self.id)

    async def pin(self):
        rest = self._state._client.rest
        await rest.pin_message(self.id)

    async def unpin(self):
        rest = self._state.client.rest
        await rest.unpin_message(self.id)

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)

        if self._reactions is not None:
            for reaction in self._reactions:
                self.reactions._add(reaction)

        if self.channel is not None:
            self.guild = self.channel.guild

        if self.guild is not None and self._member is not None:
            if self._member.get('user') is None:
                self._member['user'] = self._author
            self.author = self.guild.members._add(self._member)
        else:
            self.author = self._state._client.users._add(self._author)


class ReactionState(BaseState):
    def __init__(self, client, message):
        super().__init__(client)
        self.message = message

    def _add(self, data) -> Reaction:
        reaction = self.get(data['emoji'])
        if reaction is not None:
            reaction._update(data)
            return reaction

        reaction = Reaction.unmarshal(data)
        self._values[reaction.emoji] = reaction
        return reaction

    async def add(self, emoji):
        rest = self.client.rest
        await rest.create_reaction(self.message.channel.id, self.message.id, emoji)

    async def fetch_all(self):
        rest = self.client.rest
        data = await rest.get_reactions(self.message.channel.id, self.message.id)
        reactions = [self._add(reaction) for reaction in data]
        return reactions

    async def remove(self, emoji, user=None):
        user = _try_snowflake(user)

        rest = self.client.rest
        await rest.delete_reaction(self.message.channel.id, self.message.id, emoji, user)

    async def remove_emoji(self, emoji):
        rest = self.client.rest
        await rest.delete_reactions(self.message.channel.id, self.message.id, emoji)

    async def remove_all(self, emoji):
        rest = self.client.rest
        await rest.delete_reactions(self._message.channel.id, self._message.id)


class MessageState(BaseState):
    def __init__(self, client, channel):
        super().__init__(client)
        self.channel = channel

    def _add(self, data) -> Message:
        message = self.get(data['id'])
        if message is not None:
            message._update(data)
            return message

        message = Message.unmarshal(data, state=self, channel=self.channel)
        self._values[message.id] = message
        return message

    async def fetch(self, message_id) -> Message:
        rest = self.client.rest
        data = await rest.get_channel_message(self.channel.id, message_id)
        message = self._add(data)
        return message

    async def fetch_history(self, **kwargs):
        rest = self.client.rest
        data = await rest.get_channel_messages(self.channel.id, **kwargs)
        messages = [self._add(message) for message in data]
        return messages

    async def bulk_delete(self, messages):
        messages = [_try_snowflake(message) for message in messages]
        rest = self.client.rest
        await rest.bulk_delete_messages(self.channel.id, messages)

    async def fetch_pins(self):
        rest = self.client.rest
        await rest.get_pinned_message(self.channel.id)
