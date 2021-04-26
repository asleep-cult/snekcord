import typing as t

if t.TYPE_CHECKING:
    from .guild import Guild
    from .client import Client
    from .message import Message
    from .voice import VoiceConnection

from . import structures
from .user import User, UserState
from .enums import ChannelType
from .invite import ChannelInviteState
from .message import MessageState
from .permissions import PermissionOverwriteState
from .state import BaseState, BaseSubState
from .utils import _try_snowflake, undefined
from .voice import VoiceConnection, VoiceState


class GuildChannel(structures.GuildChannel):
    __slots__ = (
        '_state', 'guild', 'messages', 'permission_overwrites'
    )

    def __init__(self, *, state: 'ChannelState', guild: t.Optional['Guild'] = None):
        self._state = state
        self._set_guild(guild)
        self.messages = MessageState(client=self._state.client, channel=self)
        self.permission_overwrites = PermissionOverwriteState(
            client=self._state.client, channel=self)

    @property
    def parent(self) -> t.Optional['CategoryChannel']:
        return self._state.client.channels.get(self.parent_id)

    @property
    def mention(self) -> str:
        return '<#{}>'.format(self.id)

    async def delete(self) -> None:
        rest = self._state.client.rest
        await rest.delete_channel(self.id)

    def _set_guild(self, guild: t.Optional['Guild'] = None) -> None:
        if guild is not None:
            self.guild = guild

        if self.guild is not None:
            self.guild_id = self.guild.id
        else:
            self.guild = self._state.client.guilds.get(self.guild_id)

    def _update(self, *args, **kwargs) -> None:
        super()._update(*args, **kwargs)
        overwrites_seen = set()

        for overwrite in self._permission_overwrites:
            overwrite = self.permission_overwrites.append(overwrite)
            overwrites_seen.add(overwrite.id)

        for overwrite in self.permission_overwrites:
            if overwrite.id not in overwrites_seen:
                self.permission_overwrites.pop(overwrite.id)

        self._set_guild()


class TextChannel(GuildChannel, structures.TextChannel):
    __slots__ = (
        'last_pin_timestamp', 'invites'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_pin_timestamp: t.Optional[str] = None
        self.invites = ChannelInviteState(
            superstate=self._state.client.invites, channel=self)

    async def edit(self, **kwargs) -> None:
        rest = self._state.client.rest

        parent = kwargs.pop('parent', undefined)
        if parent is not undefined:
            parent = _try_snowflake(parent)

        data = await rest.modify_channel(self.id, **kwargs, parent_id=parent)
        message = self._state.append(data)
        return message

    async def send(
        self,
        content: t.Optional[str] = None,
        *,
        nonce: t.Optional[int] = None,
        tts: bool = False,
        embed: structures.Embed = None
    ) -> 'Message':
        rest = self._state.client.rest
        if embed is not None:
            embed = embed.to_dict()
        data = await rest.send_message(
            self.id, content=content, nonce=nonce, tts=tts, embed=embed)
        message = self.messages.append(data)
        return message

    async def trigger_typing(self) -> None:
        rest = self._state.client.rest
        await rest.trigger_typing(self.id)


class VoiceChannel(GuildChannel, structures.VoiceChannel):
    __slots__ = ('voice_connection',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.voice_connection: t.Optional['VoiceConnection'] = None

    async def connect(self) -> 'VoiceConnection':
        shard = self.guild.shard
        voice_state_update, voice_server_update = shard.update_voice_state(
            self.guild.id, self.id)

        state_data = await voice_state_update
        server_data = await voice_server_update

        voice_state = VoiceState.unmarshal(state_data, voice_channel=self)
        voice_server = structures.VoiceServerUpdate.unmarshal(server_data)

        self.voice_connection = VoiceConnection(
            self._state.client.loop, voice_state, voice_server)
        await self.voice_connection.connect()

        return self.voice_connection

    async def edit(self, **kwargs) -> 'VoiceChannel':
        rest = self._state.client.rest

        parent = kwargs.pop('parent', undefined)
        if parent is not undefined:
            parent = _try_snowflake(parent)

        data = await rest.modify_channel(**kwargs, parent_id=parent)
        channel = self._state.append(data, guild=self.guild)

        return channel


class CategoryChannel(GuildChannel):
    __slots__ = ()


class DMChannel(structures.DMChannel):
    __slots__ = ('_state', 'recipients', 'messages')

    def __init__(self, *, state: 'ChannelState'):
        self._state = state
        self.recipients = ChannelRecipientState(
            superstate=self._state.client.channels, channel=self)
        self.messages = MessageState(
            client=self._state.client, channel=self)

    def _update(self, *args, **kwargs) -> None:
        super()._update(*args, **kwargs)

        for recipient in self._recipients:
            user = self._state.client.users.append(recipient)
            user.dm_channel = self


class ChannelRecipientState(BaseSubState):
    def __init__(self, *, superstate: UserState, channel: DMChannel):
        super().__init__(superstate=superstate)
        self.channel = channel

    def _check_relation(self, item: User) -> bool:
        return isinstance(item, User) and item.dm_channel == self.channel

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
        ChannelType.GUILD_CATEGORY: CategoryChannel,
        13: GuildChannel,  # Just to make it shut up
        5: TextChannel # Make this one shut up too
    }

    @classmethod
    def set_guildtext_class(cls, klass: type) -> None:
        cls._channel_type_map[ChannelType.GUILD_TEXT] = klass

    @classmethod
    def set_guildvoice_class(cls, klass: type) -> None:
        cls._channel_type_map[ChannelType.GUILD_VOICE] = klass

    @classmethod
    def set_guildcategory_class(cls, klass: type) -> None:
        cls._channel_type_map[ChannelType.GUILD_CATEGORY] = klass

    @classmethod
    def set_dm_class(cls, klass: type) -> None:
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
    def __init__(self, *, superstate: ChannelState, guild: 'Guild'):
        super().__init__(superstate=superstate)
        self.guild = guild

    def _check_relation(self, item):
        return isinstance(item, GuildChannel) and item.guild == self.guild

    async def fetch_all(self) -> t.List[t.Union[TextChannel, VoiceChannel, CategoryChannel]]:
        rest = self.superstate.client.rest
        data = await rest.get_guild_channels(self.guild.id)
        channels = [self.append(channel) for channel in data]
        return channels

    async def create(self, **kwargs) -> t.List[t.Union[TextChannel, VoiceChannel, CategoryChannel]]:
        rest = self.superstate.client.rest
        parent = kwargs.pop('parent', undefined)
        if parent is not undefined:
            parent = _try_snowflake(parent)

        data = await rest.create_guild_channel(
            self.guild.id, **kwargs, parent_id=parent)
        channel = self.superstate.append(data)

        return channel

    async def modify_positions(self, positions) -> None:
        rest = self.superstate.client.rest
        await rest.modify_guild_channel_positions(self.guild.id, positions)
