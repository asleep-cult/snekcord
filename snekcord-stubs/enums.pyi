from __future__ import annotations

import typing as t

T = t.TypeVar('T')


class Enum(t.Generic[T]):
    _enum_type_: type[T]
    _enum_names_: t.ClassVar[dict[str, Enum[T]]]
    _enum_values_: t.ClassVar[dict[T, Enum[T]]]

    name: str
    value: T

    def __init__(self, name: str, value: T) -> None: ...

    def __eq__(self, other: T | Enum[T]) -> bool: ...

    def __ne__(self, other: T | Enum[T]) -> bool: ...

    @classmethod
    def get_enum(cls, value: T) -> Enum[T]: ...

    @classmethod
    def get_value(cls, enum: T | Enum[T]) -> T: ...


class ChannelType(Enum[int]):
    GUILD_TEXT: t.ClassVar[int]
    DM: t.ClassVar[int]
    GUILD_VOICE: t.ClassVar[int]
    GROUP_DM: t.ClassVar[int]
    GUILD_CATEGORY: t.ClassVar[int]
    GUILD_NEWS: t.ClassVar[int]
    GUILD_STORE: t.ClassVar[int]
    GUILD_NEWS_THREAD: t.ClassVar[int]
    GUILD_PUBLIC_THREAD: t.ClassVar[int]
    GUILD_PRIVATE_THREAD: t.ClassVar[int]
    GUILD_STAGE_VOICE: t.ClassVar[int]


class EmbedType(Enum[str]):
    RICH: t.ClassVar[str]
    IMAGE: t.ClassVar[str]
    VIDEO: t.ClassVar[str]
    GIFV: t.ClassVar[str]
    ARTICLE: t.ClassVar[str]
    LINK: t.ClassVar[str]


class MessageNotificationsLevel(Enum[int]):
    ALL_MESSAGES: t.ClassVar[int]
    ONLY_MENTIONS: t.ClassVar[int]


class ExplicitContentFilterLevel(Enum[int]):
    DISABLED: t.ClassVar[int]
    MEMBERS_WITHOUT_ROLES: t.ClassVar[int]
    ALL_MEMBERS: t.ClassVar[int]


class MFALevel(Enum[int]):
    NONE: t.ClassVar[int]
    ELEVATED: t.ClassVar[int]


class VerificationLevel(Enum[int]):
    NONE: t.ClassVar[int]
    LOW: t.ClassVar[int]
    MEDIUM: t.ClassVar[int]
    HIGH: t.ClassVar[int]
    VERY_HIGH: t.ClassVar[int]


class GuildNSFWLevel(Enum[int]):
    DEFAULT: t.ClassVar[int]
    EXPLICIT: t.ClassVar[int]
    SAFE: t.ClassVar[int]
    AGE_RESTRICTED: t.ClassVar[int]


class PremiumTier(Enum[int]):
    NONE: t.ClassVar[int]
    TIER_1: t.ClassVar[int]
    TIER_2: t.ClassVar[int]
    TIER_3: t.ClassVar[int]


class GuildFeature(Enum[str]):
    ANIMATED_ICON: t.ClassVar[str]
    BANNER: t.ClassVar[str]
    COMMERCE: t.ClassVar[str]
    COMMUNITY: t.ClassVar[str]
    DISCOVERABLE: t.ClassVar[str]
    FEATURABLE: t.ClassVar[str]
    INVITE_SPLASH: t.ClassVar[str]
    MEMBER_VERIFIVATION_GATE_ENABLED: t.ClassVar[str]
    NEWS: t.ClassVar[str]
    PARTNERED: t.ClassVar[str]
    PREVIEW_ENABLED: t.ClassVar[str]
    VANITY_URL: t.ClassVar[str]
    VERIFIED: t.ClassVar[str]
    VIP_REGIONS: t.ClassVar[str]
    WELCOME_SCREEN_ENABLED: t.ClassVar[str]
    TICKETED_EVENTS_ENABLED: t.ClassVar[str]
    MONETIZATION_ENABLED: t.ClassVar[str]
    MORE_STICKERS: t.ClassVar[str]


class IntegrationType(Enum[str]):
    TWITCH: t.ClassVar[str]
    YOUTUBE: t.ClassVar[str]
    DISCORD: t.ClassVar[str]


class IntegrationExpireBehavior(Enum[int]):
    REMOVE_ROLE: t.ClassVar[int]
    KICK: t.ClassVar[int]


class InviteTargetType(Enum[int]):
    STREAM: t.ClassVar[int]
    EMBEDDED_APPLICATION: t.ClassVar[int]


class MessageType(Enum[int]):
    DEFAULT: t.ClassVar[int]
    RECIPIENT_ADD: t.ClassVar[int]
    RECIPIENT_REMOVE: t.ClassVar[int]
    CALL: t.ClassVar[int]
    CHANNEL_NAME_CHANGE: t.ClassVar[int]
    CHANNEL_ICON_CHANGE: t.ClassVar[int]
    CHANNEL_PINNED_MESSAGE: t.ClassVar[int]
    GUILD_MEMBER_JOIN: t.ClassVar[int]
    USER_PERMIUM_GUILD_SUBSCRIPTION: t.ClassVar[int]
    USER_PERMIUM_GUILD_SUBSCRIPTION_TIER_1: t.ClassVar[int]
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_2: t.ClassVar[int]
    USER_PREMIUM_GUILD_SUBSCRIPTION_TIER_3: t.ClassVar[int]
    CHANNEL_FOLLOW_ADD: t.ClassVar[int]
    GUILD_DISCOVERY_DISQUALIFIED: t.ClassVar[int]
    GUILD_DISCOVERY_REQUALIFIED: t.ClassVar[int]
    GUILD_DISCOVERY_GRACE_PERIOD_INITIAL_WARNING: t.ClassVar[int]
    GUILD_DISCOVERY_GRACE_PERIOD_FINAL_WARNING: t.ClassVar[int]
    THREAD_CREATED: t.ClassVar[int]
    REPLY: t.ClassVar[int]
    APPLICATION_COMMAND: t.ClassVar[int]
    THREAD_STARTER_MESSAGE: t.ClassVar[int]
    GUILD_INVITE_REMINDER: t.ClassVar[int]


class PermissionOverwriteType(Enum[int]):
    ROLE: t.ClassVar[int]
    MEMBER: t.ClassVar[int]


class StageInstancePrivacyLevel(Enum[int]):
    PUBLIC: t.ClassVar[int]
    GUILD_ONLY: t.ClassVar[int]


class PremiumType(Enum[int]):
    NONE: t.ClassVar[int]
    NITRO_CLASSIC: t.ClassVar[int]
    NITRO: t.ClassVar[int]
