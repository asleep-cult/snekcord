from .channel import (
    TextChannel, 
    ChannelType,
    GuildChannel
)

from .utils import (
    JsonStructure,
    JsonField,
    JsonArray,
    Snowflake
)

from typing import (
    Union,
    Dict
)

class Guild(JsonStructure):
    id: Snowflake = JsonField('id', Snowflake, str)
    name: str = JsonField('name')
    description: str = JsonField('description')
    owner_id: Snowflake = JsonField('owner_id', Snowflake, str)
    region: str = JsonField('region')
    features: tuple = JsonField('features', tuple)
    afk_channel_id: Snowflake = JsonField('afk_channel_id', Snowflake, str)
    afk_timeout: float = JsonField('afk_timeout', float)
    system_channel_id: Snowflake = JsonField('system_channel_id', Snowflake, str)
    verification_level: int = JsonField('verification_level')
    widget_enabled: bool = JsonField('widget_enabled')
    widget_channel_id: Snowflake = JsonField('widget_channel_id', Snowflake, str)
    default_message_notifications: int = JsonField('default_message_notifications')
    mfa_level: int = JsonField('mfa_level')
    explicit_content_filter: int = JsonField('explicit_content_filter')
    max_presences: int = JsonField('max_presences')
    max_members: int = JsonField('max_members')
    max_video_channel_users: int = JsonField('max_video_channel_users')
    venity_url_code: str = JsonField('vanity_url_code')
    premium_tier: int = JsonField('premium_tier')
    premium_subscription_count: int = JsonField('premium_subscription_count')
    system_channel_flags: int = JsonField('system_channel_flags')
    preferred_locale: str = JsonField('preferred_locale')
    rules_channel_id: Snowflake = JsonField('rules_channel_id', Snowflake, str)
    public_updates_channel_id: Snowflake = JsonField('public_updates_channel_id', Snowflake, str)
    emojis: list = JsonField('emojis')
    roles: list = JsonField('roles')
    _channels: Dict[int, Union[TextChannel]] = JsonArray('channels')
    member_count: int = JsonField('approximate_member_count')
    presence_count: int = JsonField('approximate_presence_count')

    def __init__(self, *, state):
        self._state = state
        self.channels = {}
        for channel in self._channels:
            channel = state._client.channels.add(channel)
            self.channels[channel.id] = channel
        del self._channels

    def __eq__(self, other):
        return isinstance(other, Guild) and other.id == self.id

    def __str__(self):
        return self.name

class GuildState:
    def __init__(self, client):
        self._client = client
        self._guilds = {}

    def get(self, item, default=None):
        try:
            snowflake = Snowflake(item)
        except ValueError:
            return default
        return self._guilds.get(snowflake, default)

    def __getitem__(self, item):
        try:
            snowflake = Snowflake(item)
        except ValueError:
            snowflake = None
        return self._guilds[snowflake]

    def __len__(self):
        return len(self._guilds)

    async def fetch(self, channel_id):
        data = await self._client.rest.get_guild(channel_id)
        return self.add_channel(data)

    def add(self, data):
        guild = self.get(data['id'])
        if guild is not None:
            guild._update(data)
            return guild
        guild = Guild.unmarshal(data, state=self)
        self._guilds[guild.id] = guild
        return guild