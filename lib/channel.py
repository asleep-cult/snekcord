from .bases import (
    BaseObject,
    BaseState
)

from .utils import (
    JsonField,
    JsonArray,
    Snowflake
)

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
        'nsfw', 'parent_id', 'type')

    name: str = JsonField('name')
    guild_id: Snowflake = JsonField('guild_id', Snowflake, str)
    permission_overwrites = JsonField('permission_overwrites')
    position: int = JsonField('position')
    nsfw = JsonField('nsfw')
    parent_id: Snowflake = JsonField('parent_id', Snowflake, str)
    type = JsonField('type')

    def __init__(self, *, state, guild=None):
        self._state = state

        self.guild = guild or state._client.guilds.get(self.guild_id)

    @property
    def mention(self):
        return '<#{0}>'.format(self.id)


class TextChannel(GuildChannel):
    __json_slots__ = (*GuildChannel.__json_slots__, 'last_message_id')

    last_message_id: Snowflake = JsonField('last_message_id', Snowflake, str)

    def send(self, content=None, *, nonce=None, tts=False):
        return self._state._client.rest.send_message(self.id, content, nonce, tts)


class VoiceChannel(GuildChannel):
    __json_slots__ = (*GuildChannel.__json_slots__, 'bitrate', 'user_limit')

    bitrate: int = JsonField('bitrate')
    user_limit: int = JsonField('user_limit')


class CategoryChannel(GuildChannel):
    pass


class DMChannel(BaseObject):
    __json_slots__ = (*GuildChannel.__json_slots__, 'last_message_id', 'type', '_recipients', 'recipients')

    last_message_id: Snowflake = JsonField('last_message_id', Snowflake, str)
    type: int = JsonField('type')
    _recipients = JsonArray('recipients')

    def __init__(self, state):
        self._state = state
        self.recipients = {}

        for recipient in self._recipients:
            user = state._client.users.add(recipient)
            self.recipients[user.id] = user

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
        return self.add(data)

    def add(self, data, *args, **kwargs):
        channel = self.get(data['id'])
        if channel is not None:
            channel._update(data)
            return channel
        cls = _CHANNEL_TYPE_MAP.get(data['type'])
        channel = cls.unmarshal(data, *args, state=self, **kwargs)
        self._values[channel.id] = channel
        return channel
