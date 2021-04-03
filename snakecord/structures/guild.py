from typing import List

from .base import BaseObject
from ..utils import JsonArray, JsonField, JsonStructure, Snowflake, Json


class GuildWidgetChannel(BaseObject, base=False):
    __json_fields__ = {
        'name': JsonField('name'),
        'position': JsonField('position'),
    }

    name: str
    position: int


class GuildWidgetMember(BaseObject, base=False):
    __json_fields__ = {
        'username': JsonField('username'),
        'discriminator': JsonField('discriminator'),
        'avatar': JsonField('avatar'),
        'avatar_url': JsonField('avatar_url'),
    }

    username: str
    discriminator: str
    avatar: str
    avatar_url: str


class GuildWidget(BaseObject, base=False):
    __json_fields__ = {
        'name': JsonField('name'),
        'instant_invite': JsonField('instant_invite'),
        'channels': JsonArray('channels', struct=GuildWidgetChannel),
        'members': JsonArray('members', struct=GuildWidgetMember),
        'presence_count': JsonField('presence_count'),
    }

    name: str
    instant_invite: str
    channels: List[GuildWidgetChannel]
    members: List[GuildWidgetMember]
    presence_count: int


class GuildWidgetSettings(JsonStructure, base=False):
    __json_fields__ = {
        'enabled': JsonField('enabled'),
        'channel_id': JsonField('channel_id'),
    }

    enabled: bool
    channel_id: Snowflake


class GuildPreview(BaseObject, base=False):
    # Basically a partial guild?
    __json_fields__ = {
        'name': JsonField('name'),
        'icon': JsonField('icon'),
        'splash': JsonField('splash'),
        'discovery_splash': JsonField('discovery_splash'),
        '_emojis': JsonArray('emojis'),
        'features': JsonArray('features'),
        'member_count': JsonField('approximate_member_count'),
        'presence_count': JsonField('approximate_presence_count'),
        'description': JsonField('description'),
    }

    name: str
    icon: str
    splash: str
    discovery_splash: str
    _emojis: List[Json]
    features: List[str]
    member_count: int
    presence_count: int
    description: str


class Guild(JsonStructure, base=False):
    __json_fields__ = {
        'icon_hash': JsonField('icon_hash'),
        '_owner': JsonField('owner'),
        'owner_id': JsonField('owner_id', Snowflake, str),
        'permissions': JsonField('permissions'),
        'region': JsonField('region'),
        'afk_channel_id': JsonField('afk_channel_id', Snowflake, str),
        'afk_timeout': JsonField('afk_timeout'),
        'widget_enabled': JsonField('widget_enabled'),
        'widget_channel_id': JsonField('widget_channel_id', Snowflake, str),
        'verification_level': JsonField('verification_level'),
        'default_message_notifications': JsonField('default_message_notifications'),
        'explicit_content_filter': JsonField('explicit_content_filter'),
        '_roles': JsonArray('roles'),
        'mfa_level': JsonField('mfa_level'),
        'application_id': JsonField('application_id', Snowflake, str),
        'system_channel_id': JsonField('system_channel_id', Snowflake, str),
        'system_channel_flags': JsonField('system_channel_flags'),
        'rules_channel_id': JsonField('rules_channel_id', Snowflake, str),
        'joined_at': JsonField('joined_at'),
        'large': JsonField('large'),
        'unavailable': JsonField('unavailable'),
        'member_count': JsonField('member_count'),
        '_voice_states': JsonArray('voice_states'),
        '_members': JsonArray('members'),
        '_channels': JsonArray('channels'),
        '_presences': JsonArray('presences'),
        'max_presences': JsonField('max_presences'),
        'max_members': JsonField('max_members'),
        'vanity_url_code': JsonField('vanity_url_code'),
        'banner': JsonField('banner'),
        'premium_tier': JsonField('permium_tier'),
        'premium_subscription_count': JsonField('premium_subscription_count'),
        'preferred_locale': JsonField('preferred_locale'),
        'public_updates_channel_id': JsonField('public_updates_channel_id', Snowflake, str),
        'max_video_channel_users': JsonField('max_video_channel_users'),
    }

    icon_hash: str
    _owner: Json
    owner_id: Snowflake
    permissions: int  # ?
    region: str
    afk_channel_id: Snowflake
    afk_timeout: int
    widget_enabled: bool
    widget_channel_id: Snowflake
    verification_level: int  # TODO: enum
    default_message_notifications: int  # TODO: enum
    explicit_content_filter: int  # TODO: enum
    _roles: List[Json]
    mfa_level: int
    application_id: Snowflake
    system_channel_id: Snowflake
    system_channel_flags: int
    rules_channel_id: Snowflake
    joined_at: str
    large: bool
    unavailable: bool
    member_count: int
    _voice_states: List[Json]
    _members: List[Json]
    _channels: List[Json]
    _presences: List[Json]
    max_presences: int
    max_members: int
    vanity_url_code: str
    banner: str
    premium_tier: int
    premium_subscription_count: int
    preferred_locale: str
    public_updates_channel_id: Snowflake
    max_video_channel_users: int


class GuildBan(JsonStructure, base=False):
    __json_fields__ = {
        'reason': JsonField('reason'),
        '_user': JsonField('user'),
    }

    reason: str
    _user: Json
