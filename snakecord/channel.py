from . import structures
from .enums import ChannelType
from .invite import ChannelInviteState
from .message import MessageState
from .permissions import PermissionOverwriteState
from .state import BaseState, BaseSubState
from .utils import _try_snowflake, undefined
from .voice import VoiceConnection, VoiceState


class GuildChannel(structures.GuildChannel):
    __slots__ = (
        '_state', 'id', 'name', 'guild_id', 'permission_overwrites',
        'position', 'nsfw', 'parent_id', 'type'
    )

    def __init__(self, *, state, guild=None):
        self._state = state
        self.guild = guild
        self.messages: MessageState = MessageState(self._state.client, self)
        self.permission_overwrites = PermissionOverwriteState(self._state.client, self)

        if self.guild is not None:
            self.guild_id = guild.id

    @property
    def mention(self) -> str:
        return '<#{0}>'.format(self.id)

    async def delete(self) -> None:
        rest = self._state.client.rest
        await rest.delete_channel(self.id)

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)
        overwrites_seen = set()

        for overwrite in self._permission_overwrites:
            overwrite = self.permission_overwrites.append(overwrite)
            overwrites_seen.add(overwrite.id)

        for overwrite in self.permission_overwrites:
            if overwrite.id not in overwrites_seen:
                self.permission_overwrites.pop(overwrite.id)

        if self.guild is None:
            self.guild = self._state.client.guilds.get(self.guild_id)

        self.parent = self._state.get(self.parent_id)


class TextChannel(GuildChannel, structures.TextChannel):
    __slots__ = (
        *GuildChannel.__slots__, 'last_message_id', 'last_pin_timestamp'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_pin_timestamp = None
        self.invites = ChannelInviteState(self._state.client.invites, self)

    async def edit(self, **kwargs) -> None:
        rest = self._state.client.rest

        parent = kwargs.pop('parent', undefined)
        if parent is not undefined:
            parent = _try_snowflake(parent)

        data = await rest.modify_channel(self.id, **kwargs, parent_id=parent)
        message = self._state.append(data)
        return message

    async def send(self, content=None, *, nonce=None, tts=False, embed=None) -> None:
        rest = self._state.client.rest
        if embed is not None:
            embed = embed.to_dict()
        data = await rest.send_message(self.id, content=content, nonce=nonce, tts=tts, embed=embed)
        message = self.messages.append(data)
        return message

    async def trigger_typing(self):
        rest = self._state.client.rest
        await rest.trigger_typing(self.id)


class VoiceChannel(GuildChannel, structures.VoiceChannel):
    __slots__ = (*GuildChannel.__slots__, 'bitrate', 'user_limit')

    async def connect(self):
        shard = self.guild.shard
        voice_state_update, voice_server_update = \
            await shard.update_voice_state(self.guild.id, self.id)

        state_data = await voice_state_update
        server_data = await voice_server_update

        voice_state = VoiceState.unmarshal(state_data.data, voice_channel=self)
        voice_server = structures.VoiceServerUpdate.unmarshal(server_data.data)

        self.voice_connection = VoiceConnection(voice_state, voice_server)
        await self.voice_connection.connect()

        return self.voice_connection

    async def edit(self, **kwargs):
        rest = self._state.client.rest

        parent = kwargs.pop('parent', undefined)
        if parent is not undefined:
            parent = _try_snowflake(parent)

        resp = await rest.modify_channel(**kwargs, parent_id=parent)
        data = await resp.json()
        channel = self._state.append(data, guild=self.guild)
        return channel


class CategoryChannel(GuildChannel):
    __slots__ = GuildChannel.__slots__


class DMChannel(structures.DMChannel):
    __slots__ = (
        'last_message_id', 'type', '_recipients', 'recipients'
    )

    def __init__(self, state):
        self._state: ChannelState = state
        self.recipients = ChannelRecipientState(self._state.client, channel=self)

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)

        for recipient in self._recipients:
            self.recipients.append(recipient)


class ChannelRecipientState(BaseState):
    def __init__(self, client, *, channel: DMChannel):
        super().__init__(client)
        self.channel = channel

    def append(self, data):
        user = self.client.users.append(data)
        self._items[user.id] = user
        return user

    async def add(self, user, access_token, *, nick):
        user = _try_snowflake(user)
        rest = self.client.rest
        await rest.add_dm_recipient(self.channel.id, user, access_token, nick)

    async def remove(self, user):
        user = _try_snowflake(user)
        rest = self.client.rest
        await rest.remove_dm_recipient(self.channel.id, user)


class ChannelState(BaseState):
    _channel_type_map = {
        ChannelType.GUILD_TEXT: TextChannel,
        ChannelType.DM: DMChannel,
        ChannelType.GUILD_VOICE: VoiceChannel,
        ChannelType.GUILD_CATEGORY: CategoryChannel
    }

    @classmethod
    def set_guildtext_class(cls, klass):
        cls._channel_type_map[ChannelType.GUILD_TEXT] = klass

    @classmethod
    def set_guildvoice_class(cls, klass):
        cls._channel_type_map[ChannelType.GUILD_VOICE] = klass

    @classmethod
    def set_guildcategory_class(cls, klass):
        cls._channel_type_map[ChannelType.GUILD_CATEGORY] = klass

    @classmethod
    def set_dm_class(cls, klass):
        cls._channel_type_map[ChannelType.DM] = klass

    def append(self, data, *args, **kwargs):
        channel = self.get(data['id'])
        if channel is not None:
            channel._update(data)
            return channel

        cls = self._channel_type_map[data['type']]
        channel = cls.unmarshal(data, *args, **kwargs, state=self)
        self._items[channel.id] = channel
        return channel

    async def fetch(self, channel_id):
        rest = self.client.rest
        channel = await rest.get_channel(channel_id)
        return self.append(channel)


class GuildChannelState(BaseSubState):
    def __init__(self, superstate, guild):
        super().__init__(superstate)
        self.guild = guild

    def _check_relation(self, item):
        return isinstance(item, GuildChannel) and item.guild == self.guild

    async def fetch_all(self):
        rest = self.superstate.client.rest
        data = await rest.get_guild_channels(self.guild.id)
        channels = [self.append(channel) for channel in data]
        return channels

    async def create(self, **kwargs):
        rest = self.superstate.client.rest
        parent = kwargs.pop('parent', undefined)
        if parent is not undefined:
            parent = _try_snowflake(parent)

        await rest.create_guild_channel(self.guild.id, **kwargs, parent_id=parent)

    async def modify_positions(self, positions):
        rest = self.superstate.client.rest
        await rest.modify_guild_channel_positions(self.guild.id, positions)
