from .utils import (
    JsonStructure,
    JsonField,
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

class GuildChannel(JsonStructure):
    id: Snowflake = JsonField('id', Snowflake, str)
    name = JsonField('name')
    guild_id: Snowflake = JsonField('guild_id', Snowflake, str)
    permission_overwrites = JsonField('permission_overwrites')
    position = JsonField('position')
    nsfw = JsonField('nsfw')
    parent_id: Snowflake = JsonField('parent_id', Snowflake, str)
    type = JsonField('type')

    def __init__(self, *, state):
        self._state = state

    @property
    def mention(self):
        return '<#{0}>'.format(self.id)

class TextChannel(GuildChannel):
    last_message_id = JsonField('last_message_id', int, str)

    def send(self, content=None, *, nonce=None, tts=False):
        return self.manager.rest.send_message(self.id, content, nonce, tts)

class VoiceChannel(GuildChannel):
    bitrate = JsonField('bitrate')
    user_limit = JsonField('user_limit')

class CategoryChannel(GuildChannel):
    pass

class DMChannel(JsonStructure):
    id = JsonField('id')
    last_message_id = JsonField('last_message_id', int, str)
    type = JsonField('type')
    recepients = JsonField('recepients')

    def __init__(self, state):
        self._state = state

CHANNEL_TYPE_MAP = {
    ChannelType.GUILD_TEXT: TextChannel,
    ChannelType.DM: DMChannel,
    ChannelType.GUILD_VOICE: VoiceChannel,
    ChannelType.GUILD_CATEGORY: CategoryChannel
}

class ChannelState:
    def __init__(self, client):
        self._client = client
        self._channels = {}

    def get(self, item, default=None):
        try:
            snowflake = Snowflake(item)
        except ValueError:
            return default
        return self._channels.get(snowflake, default)

    def __getitem__(self, item):
        try:
            snowflake = Snowflake(item)
        except ValueError:
            snowflake = None
        return self._channels[snowflake]

    def __len__(self):
        return len(self._channels)

    async def fetch(self, channel_id):
        data = await self._client.rest.get_channel(channel_id)
        return self.add_channel(data)

    def add(self, data):
        channel = self.get(data['id'])
        if channel is not None:
            channel._update(data)
            return channel
        cls = CHANNEL_TYPE_MAP.get(data['type'])
        channel = cls.unmarshal(data, state=self)
        self._channels[channel.id] = channel
        return channel
