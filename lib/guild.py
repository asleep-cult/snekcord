from .utils import (
    JsonStructure,
    JsonField
)

class Guild(JsonStructure):
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