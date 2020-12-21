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

def guild_channel_unmarshall(data):
    channel_type = data.get('type')
    if channel_type is None:
        raise Exception('No channel Type')
    elif channel_type == ChannelType.GUILD_TEXT:
        return TextChannel.unmarshal(data, init_class=False)

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
    channels: Dict[int, Union[TextChannel]] = JsonArray('channels', unmarshal_callable=guild_channel_unmarshall, marshal_callable=JsonStructure.to_dict)
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

    def get_channel(self, channel_id):
        return self.channels.get(channel_id)
