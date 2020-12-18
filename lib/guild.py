from .channel import (
    TextChannel, 
    ChannelType,
    GuildChannel
)

from .utils import (
    JsonStructure,
    JsonField,
    JsonArray
)

from typing import (
    Union,
    Dict
)

def guild_channel_unmarshall(data):
    channel_type = data.get('type')
    if channel_type is None:
        raise Exception('No channel Type')
    elif channel_type == ChannelType.GUILD_TEXT:
        return TextChannel.unmarshal(data, init_class=False)

class Guild(JsonStructure):
<<<<<<< HEAD

    id: int = JsonField(int, 'id')
    name: str = JsonField(str, 'name')
    description: str = JsonField(str, 'description')
    owner_id: int = JsonField(int, 'owner_id')
    region: str = JsonField(str, 'region')
    features: tuple = JsonField(tuple, 'features')
    afk_channel_id: int = JsonField(int, 'afk_channel_id')
    afk_timeout: float = JsonField(float, 'afk_timeout')
    system_channel_id: int = JsonField(int, 'system_channel_id')
    verification_level: int = JsonField(int, 'verification_level')
    widget_enabled: bool = JsonField(bool, 'widget_enabled')
    widget_channel_id: int = JsonField(int, 'widget_channel_id')
    default_message_notifications: int = JsonField(int, 'default_message_notifications')
    mfa_level: int = JsonField(int, 'mfa_level')
    explicit_content_filter: int = JsonField(int, 'explicit_content_filter')
    max_presences: int = JsonField(int, 'max_presences')
    max_members: int = JsonField(int, 'max_members')
    max_video_channel_users: int = JsonField(int, 'max_video_channel_users')
    venity_url_code: str = JsonField(str, 'vanity_url_code')
    premium_tier: int = JsonField(int, 'premium_tier')
    premium_subscription_count: int = JsonField(int, 'premium_subscription_count')
    system_channel_flags: int = JsonField(int, 'system_channel_flags')
    preferred_locale: str = JsonField(str, 'preferred_locale')
    rules_channel_id: int = JsonField(int, 'rules_channel_id')
    public_updates_channel_id: int = JsonField(int, 'public_updates_channel_id')
    emojis: tuple = JsonField(tuple, 'emojis')
    roles: tuple = JsonField(tuple, 'roles')
    member_count: int = JsonField(int, 'approximate_member_count')
    presence_count: int = JsonField(int, 'approximate_presence_count')

    def __init__(self, *, manager):
        self._manager = manager

    async def fetch_member(self, user_id):
        return await self._manager.rest.get_member(user_id, self.id)

=======
    id: int = JsonField('id', int, str)
    name: str = JsonField('name')
    description: str = JsonField('description')
    owner_id: int = JsonField('owner_id', int, str)
    region: str = JsonField('region')
    features: tuple = JsonField('features', tuple)
    afk_channel_id: int = JsonField('afk_channel_id', int, str)
    afk_timeout: float = JsonField('afk_timeout', float)
    system_channel_id: int = JsonField('system_channel_id', int, str)
    verification_level: int = JsonField('verification_level')
    widget_enabled: bool = JsonField('widget_enabled')
    widget_channel_id: int = JsonField('widget_channel_id', int, str)
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
    rules_channel_id: int = JsonField('rules_channel_id', int, str)
    public_updates_channel_id: int = JsonField('public_updates_channel_id', int, str)
    emojis: list = JsonField('emojis')
    roles: list = JsonField('roles')
    channels: Dict[int, Union[TextChannel]] = JsonArray('channels', unmarshal_callable=guild_channel_unmarshall, marshal_callable=GuildChannel.to_dict)
    member_count: int = JsonField('approximate_member_count')
    presence_count: int = JsonField('approximate_presence_count')

    def __init__(self, *, manager):
        self._manager = manager
        channels = self.channels
        self.channels = {}
        for channel in channels:
            if channel is not None:
                channel.__init__(manager)
                self.channels[channel.id] = channel
        manager._channels.update(self.channels)

    def get_channel(self, channel_id):
        return self.channels.get(channel_id)
>>>>>>> e810744b1df8f73a495827a81b82bb0d3316a894
