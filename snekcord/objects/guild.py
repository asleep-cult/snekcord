import enum

from .base import SnowflakeObject
from .emoji import CustomEmoji
from .. import json

__all__ = (
    'GuildMessageNotifications',
    'GuildMFALevel',
    'GuildVerificationLevel',
    'GuildNSFWLevel',
    'GuildExplicitContentFilter',
    'GuildPremiumTier',
    'GuildSystemChannelFlags',
    'Guild',
)


class GuildMessageNotifications(enum.IntEnum):
    ALL_MESSAGES = 0
    ONLY_MENTIONS = 1


class GuildMFALevel(enum.IntEnum):
    NONE = 0
    ELEVATED = 1


class GuildVerificationLevel(enum.IntEnum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4


class GuildNSFWLevel(enum.IntEnum):
    DEFAULT = 0
    EXPLICIT = 1
    SAFE = 2
    AGE_RESTRICTED = 3


class GuildExplicitContentFilter(enum.IntEnum):
    DISABLED = 0
    MEMBERS_WITH_ROLES = 1
    ALL_MEMBERS = 2


class GuildPremiumTier(enum.IntEnum):
    NONE = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


class GuildSystemChannelFlags(enum.IntFlag):
    SUPPRESS_JOIN_NOTIFICATIONS = 1 << 0
    SUPPRESS_PREMIUM_SUBSCRIPTIONS = 1 << 1
    SUPPRESS_GUILD_REMINDER_NOTIFICATIONS = 1 << 2
    SUPPRESS_JOIN_NOTIFICATION_REPLIES = 1 << 3


class GuildFeature(enum.Enum):
    ANIMATED_ICON = 'ANIMATED_ICON'
    BANNER = 'BANNER'
    COMMERCE = 'COMMERCE'
    COMMUNITY = 'COMMUNITY'
    DISCOVERABLE = 'DISCOVERABLE'
    FEATURABLE = 'FEATURABLE'
    INVITE_SPLASH = 'INVITE_SPLASH'
    MEMBER_VERIFICATION_GATE_ENABLED = 'MEMBER_VERIFICATION_GATE_ENABLED'
    MONETIZATION_ENABLED = 'MONETIZATION_ENABLED'
    MORE_STICKERS = 'MORE_STICKERS'
    NEWS = 'NEWS'
    PARTNERED = 'PARTNERED'
    PREVIEW_ENABLED = 'PREFIEW_ENABLED'
    PRIVATE_THREADS = 'PRIVATE_THREADS'
    ROLE_ICONS = 'ROLE_ICONS'
    SEVEN_DAY_THREAD_ARCHIVE = 'SEVEN_DAY_THREAD_ARCHIVE'
    THREE_DAY_THREAD_ARCHIVE = 'THREE_DAY_THREAD_ARCHIVE'
    TICKETED_EVENTS_ENABLED = 'TICKETED_EVENTS_ENABLED'
    VANITY_URL = 'VANITY_URL'
    VERIFIED = 'VERIFIED'
    VIP_REGIONS = 'VIP_REGIONS'
    WELCOME_SCREEN_ENABLED = 'WELCOME_SCREEN_ENABLED'


class Guild(SnowflakeObject):
    __slots__ = (
        'roles',
        'emojis',
        'members',
        'channels',
        'owner',
        'afk_channel',
        'widget_channel',
        'system_channel',
        'rules_channel',
        'public_updates_channel',
    )

    name = json.JSONField('name')
    icon = json.JSONField('icon')
    splash = json.JSONField('splash')
    discovery_splash = json.JSONField('discovery_splash')
    afk_timeout = json.JSONField('afk_timeout')
    features = json.JSONArray('features', GuildFeature)
    system_channel_flags = json.JSONField('system_channel_flags', GuildSystemChannelFlags)
    verification_level = json.JSONField('verification_level', GuildVerificationLevel)
    message_notifications_level = json.JSONField(
        'default_message_notifications', GuildMessageNotifications
    )
    explicit_content_filter = json.JSONField('explicit_content_filter', GuildExplicitContentFilter)
    mfa_level = json.JSONField('mfa_level', GuildMFALevel)
    nsfw_level = json.JSONField('nsfw_level', GuildNSFWLevel)
    premium_tier = json.JSONField('premium_tier', GuildPremiumTier)
    large = json.JSONField('large')
    unavailable = json.JSONField('unavailable')
    max_presences = json.JSONField('max_presences')
    max_members = json.JSONField('max_members')
    description = json.JSONField('description')
    preferred_locale = json.JSONField('preferred_locale')

    def __init__(self, *, state) -> None:
        super().__init__(state=state)

        self.roles = self.client.create_role_state(guild=self)
        self.emojis = self.client.create_emoji_state(guild=self)
        self.members = self.client.create_member_state(guild=self)
        self.channels = self.client.create_channel_state(guild=self)

        self.owner = self.client.users.wrap_id(None)
        self.afk_channel = self.client.channels.wrap_id(None)
        self.widget_channel = self.client.channels.wrap_id(None)
        self.system_channel = self.client.channels.wrap_id(None)
        self.rules_channel = self.client.channels.wrap_id(None)
        self.public_updates_channel = self.client.channels.wrap_id(None)

    async def update_roles(self, roles):
        upserted = set()
        for role in roles:
            upserted.add(await self.roles.upsert(role))

        for role in self.roles:
            if role not in upserted:
                self.roles.cache.pop(role.id)

    async def update_members(self, members):
        for member in members:
            await self.members.upsert(member)

    async def update_channels(self, channels):
        upserted = set()
        for channel in channels:
            channel['guild_id'] = Guild.id.deconstruct(self.id)
            upserted.add(await self.channels.upsert(channel))

        for channel in self.channels:
            if channel not in upserted:
                self.channels.cache.pop(channel.id)

    async def update_emojis(self, emojis):
        upserted = set()
        for emoji in emojis:
            emoji['guild_id'] = CustomEmoji.id.deconstruct(self.id)
            upserted.add(await self.emojis.upsert(emoji))

        for emoji in self.emojis:
            if emoji not in upserted:
                self.emojis.cache.pop(emoji.id)
