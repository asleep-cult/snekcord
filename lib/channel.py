from .user import User

from .message import (
    MessageState,
    Message
)

from .bases import (
    BaseObject,
    BaseState
)

from .utils import (
    JsonField,
    JsonArray,
    Snowflake
)

from .voice import (
    VoiceConnection,
    VoiceState,
    VoiceServerUpdate
)

from typing import (
    Union,
    Iterable,
    List,
    TYPE_CHECKING
)

if TYPE_CHECKING:
    from .guild import Guild


class ChannelType:
    GUILD_TEXT = 0	
    DM = 1	
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6


class GuildChannel(BaseObject):
    __json_slots__ = (
        '_state', 'id', 'name', 'guild_id', 'permission_overwrites', 'position',
        'nsfw', 'parent_id', 'type'
    )

    name: str = JsonField('name')
    guild_id: Snowflake = JsonField('guild_id', Snowflake, str)
    permission_overwrites = JsonField('permission_overwrites')
    position: int = JsonField('position')
    nsfw = JsonField('nsfw')
    parent_id: Snowflake = JsonField('parent_id', Snowflake, str)
    type = JsonField('type')

    def __init__(self, *, state, guild=None):
        self._state: ChannelState = state
        self.messages: Iterable[Message] = MessageState(state._client, self)

        self.guild: 'Guild' = guild or state._client.guilds.get(self.guild_id)

    @property
    def mention(self) -> str:
        return '<#{0}>'.format(self.id)

    async def delete(self) -> None:
        resp = await self._state._client.rest.delete_channel(self.id)


class TextChannel(GuildChannel):
    __json_slots__ = (*GuildChannel.__json_slots__, 'last_message_id')

    last_message_id: Snowflake = JsonField('last_message_id', Snowflake, str)

    async def edit(
        self, 
        *, 
        name=None, 
        channel_type=None, 
        position=None, 
        topic=None, 
        nsfw=None, 
        slowmode=None, 
        permission_overwrites=None, 
        category=None
    ) -> None:
        rest = self._state._client.rest
        if category is not None:
            category = category.id
        resp = await rest.modify_channel(
            self.id, name=name, channel_type=channel_type, 
            position=position, topic=topic, nsfw=nsfw, 
            slowmode=slowmode, permission_overwrites=permission_overwrites,
            category=category
        )
        # todo... return channel

    async def send(self, content=None, *, nonce=None, tts=False, embed=None) -> None:
        rest = self._state._client.rest
        if embed is not None:
            embed = embed.to_dict()
        resp = await rest.send_message(self.id, content=content, nonce=nonce, tts=tts, embed=embed)
        # todo... return message


class VoiceChannel(GuildChannel):
    __json_slots__ = (*GuildChannel.__json_slots__, 'bitrate', 'user_limit')

    bitrate: int = JsonField('bitrate')
    user_limit: int = JsonField('user_limit')

    async def connect(self):
        voice_state_update, voice_server_update = await self.guild.shard.update_voice_state(self.guild.id, self.id)
        state_data = await voice_state_update
        server_data = await voice_server_update
        voice_state = VoiceState.unmarshal(state_data.data, voice_channel=self)
        voice_server = VoiceServerUpdate.unmarshal(server_data.data)
        self.voice_connection = VoiceConnection(voice_state, voice_server)
        await self.voice_connection.connect()
        return self.voice_connection

    async def edit(
        self,
        channel_id,
        *,
        name=None,
        channel_type=None,
        position=None,
        topic=None,
        nsfw=None,
        bitrate=None,
        user_limit=None,
        permission_overwrites=None,
        parent_id=None
    ):
        rest = self._state._client.rest
        resp = await rest.modify_channel(
            self.id, name=name, channel_type=channel_type,
            position=position, topic=topic, nsfw=nsfw, 
            bitrate=bitrate, user_limit=user_limit, 
            permission_overwrites=permission_overwrites,
            parent_id=parent_id
        )
        data = await resp.json()
        channel = self._state._add(data, guild=self.guild)
        return channel


class CategoryChannel(GuildChannel):
    async def edit(
        self, 
        *, 
        name=None, 
        channel_type=None, 
        position=None, 
        topic=None, 
        nsfw=None, 
        slowmode=None, 
        permission_overwrites=None, 
    ) -> None:
        rest = self._state._client.rest
        if category is not None:
            category = category.id
        resp = await rest.modify_channel(
            self.id, name=name, channel_type=channel_type, 
            position=position, topic=topic, nsfw=nsfw, 
            slowmode=slowmode, permission_overwrites=permission_overwrites,
        )


class DMChannel(BaseObject):
    __json_slots__ = (*GuildChannel.__json_slots__, 'last_message_id', 'type', '_recipients', 'recipients')

    last_message_id: Snowflake = JsonField('last_message_id', Snowflake, str)
    type: int = JsonField('type')
    _recipients = JsonArray('recipients')

    def __init__(self, state):
        self._state: ChannelState = state
        self.recipients: List[User] = []

        for recipient in self._recipients:
            user = state._client.users._add(recipient)
            self.recipients.append(user)

        del self._recipients


_CHANNEL_TYPE_MAP = {
    ChannelType.GUILD_TEXT: TextChannel,
    ChannelType.DM: DMChannel,
    ChannelType.GUILD_VOICE: VoiceChannel,
    ChannelType.GUILD_CATEGORY: CategoryChannel
}


class ChannelState(BaseState):
    async def fetch(self, channel_id):
        data = await self._client.rest.get_channel(channel_id)
        return self._add(data)

    def _add(self, data, *args, **kwargs):
        channel = self.get(data['id'])
        if channel is not None:
            channel._update(data)
            return channel
        cls = _CHANNEL_TYPE_MAP.get(data['type'])
        channel = cls.unmarshal(data, *args, state=self, **kwargs)
        self._values[channel.id] = channel
        return channel

_Channel = Union[DMChannel, CategoryChannel, VoiceChannel, TextChannel, GuildChannel]
