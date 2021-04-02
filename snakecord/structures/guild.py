from .base import BaseObject
from ..utils import JsonArray, JsonField, JsonStructure, Snowflake


class GuildWidgetChannel(BaseObject, base=True):
    __json_fields__ = {
        'name': JsonField('name'),
        'poosition': JsonField('position'),
    }


class GuildWidgetMember(BaseObject, base=True):
    __json_fields__ = {
        'username': JsonField('username'),
        'discriminator': JsonField('discriminator'),
        'avatar': JsonField('avatar'),
        'avatar_url': JsonField('avatar_url'),
    }


class GuildWidget(BaseObject, base=True):
    __json_fields__ = {
        'name': JsonField('name'),
        'instant_invite': JsonField('instant_invite'),
        'channels': JsonArray('channels', struct=GuildWidgetChannel),
        'members': JsonArray('members', struct=GuildWidgetMember),
        'presence_count': JsonField('presence_count'),
    }


class GuildWidgetSettings(JsonStructure, base=True):
    __json_fields__ = {
        'enabled': JsonField('enabled'),
        'channel_id': JsonField('channel_id'),
    }


class GuildPreview(BaseObject, base=True):
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


class Guild(JsonStructure, base=True):
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


class GuildBan(JsonStructure, base=True):
    __json_fields__ = {
        'reason': JsonField('reason'),
        '_user': JsonField('user'),
    }
