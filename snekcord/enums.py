from .utils.enum import Enum


class ChannelType(Enum[int]):
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6
    GUILD_NEWS_THREAD = 10
    GUILD_PUBLIC_THREAD = 11
    GUILD_PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13


class EmbedType(Enum[str]):
    RICH = 'rich'
    IMAGE = 'image'
    VIDEO = 'video'
    GIFV = 'gifv'
    ARTICLE = 'article'
    LINK = 'link'


class MessageNotificationsLevel(Enum[int]):
    ALL_MESSAGES = 0
    ONLY_MENTIONS = 1


class ExplicitContentFilterLevel(Enum[int]):
    DISABLED = 0
    MEMBERS_WITHOUT_ROLES = 1
    ALL_MEMBERS = 2


class MFALevel(Enum[int]):
    NONE = 0
    ELEVATED = 1


class VerificationLevel(Enum[int]):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4


class GuildNSFWLevel(Enum[int]):
    DEFAULT = 0
    EXPLICIT = 1
    SAFE = 2
    AGE_RESTRICTED = 3


class PremiumTier(Enum[int]):
    NONE = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


class GuildFeature(Enum[str]):
    ANIMATED_ICON = 'ANIMATED_ICON'
    BANNER = 'BANNER'
    COMMERCE = 'COMMERCE'
    COMMUNITY = 'COMMUNITY'
    DISCOVERABLE = 'DISCOVERABLE'
    FEATURABLE = 'FEATURABLE'
    INVITE_SPLASH = 'INVITE_SPLASH'
    MEMBER_VERIFIVATION_GATE_ENABLED = 'MEMBER_VEFIFICATION_GATE_ENNABLED'
    NEWS = 'NEWS'
    PARTNERED = 'PARTNERED'
    PREVIEW_ENABLED = 'PREVIEW_ENABLED'
    VANITY_URL = 'VANITY_URL'
    VERIFIED = 'VERIFIED'
    VIP_REGIONS = 'VIP_REGIONS'
    WELCOME_SCREEN_ENABLED = 'WELCOME_SCREEN_ENABLED'
    TICKETED_EVENTS_ENABLED = 'TICKETED_EVENTS_ENABLED'
    MONETIZATION_ENABLED = 'MONETIZATION_ENABLED'
    MORE_STICKERS = 'MORE_STICKERS'


class IntegrationType(Enum[str]):
    TWITCH = 'twitch'
    YOUTUBE = 'youtube'
    DISCORD = 'discord'


class IntegrationExpireBehavior(Enum[int]):
    REMOVE_ROLE = 0
    KICK = 1


class InviteTargetType(Enum[int]):
    STREAM = 1
    EMBEDDED_APPLICATION = 2


class MessageType(Enum[int]):
    DEFAULT = 0
    RECIPIENT_ADD = 1
    RECIPIENT_REMOVE = 2
    CALL = 3
    CHANNEL_NAME_CHANGE = 4
    CHANNEL_ICON_CHANGE = 5
    CHANNEL_PINNED_MESSAGE = 6
    GUILD_MEMBER_JOIN = 7
    USER_PERMIUM_GUILD_SUBSCRIPTION = 8
    USER_PERMIUM_GUILD_SUBSCRIPTION_TIER_1 = 9
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2 = 10
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3 = 11
    CHANNEL_FOLLOW_ADD = 12
    GUILD_DISCOVERY_DISQUALIFIED = 14
    GUILD_DISCOVERY_REQUALIFIED = 15
    GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING = 16
    GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING = 17
    THREAD_CREATED = 18
    REPLY = 19
    APPLICATION_COMMAND = 20
    THREAD_STARTER_MESSAGE = 21
    GUILD_INVITE_REMINDER = 22


class PermissionOverwriteType(Enum[int]):
    ROLE = 0
    MEMBER = 1


class StageInstancePrivacyLevel(Enum[int]):
    PUBLIC = 1
    GUILD_ONLY = 2


class PremiumType(Enum[int]):
    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2
