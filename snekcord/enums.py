class Enum:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __init_subclass__(cls):
        cls._enum_names_ = {}
        cls._enum_values_ = {}

        for key, value in cls.__dict__.items():
            if not key.startswith('_') and isinstance(value, cls._enum_type_):
                enum = cls(key, value)
                cls._enum_names_[key] = enum
                cls._enum_values_[value] = enum

    def __class_getitem__(cls, klass):
        if isinstance(klass, type):
            return type(cls.__name__, (cls,), {'_enum_type_': klass})
        return klass

    def __repr__(self):
        return f'<{self.__class__.__name__} name={self.name}, value={self.value!r}>'

    def __eq__(self, value):
        if isinstance(value, self.__class__):
            value = value.value

        if not isinstance(value, self._enum_type_):
            return NotImplemented

        return self.value == value

    def __ne__(self, value):
        if isinstance(value, self.__class__):
            value = value.value

        if not isinstance(value, self._enum_type_):
            return NotImplemented

        return self.value != value

    @classmethod
    def get_enum(cls, value):
        try:
            return cls._enum_values_[value]
        except KeyError:
            return cls('undefined', value)

    @classmethod
    def get_value(cls, enum):
        if isinstance(enum, cls):
            return enum.value
        elif isinstance(enum, cls._enum_type_):
            return enum
        raise ValueError(f'{enum!r} is not a valid {cls.__name__}')


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


class VideoQualityMode(Enum[int]):
    AUTO = 1
    FULL = 2


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


class StickerType(Enum[int]):
    STANDARD = 1
    GUILD = 2


class StickerFormatType(Enum[int]):
    PNG = 1
    APNG = 2
    LOTTIE = 3


class MessageActivityType(Enum[int]):
    JOIN = 1
    SPECTATE = 2
    LISTEN = 3
    JOIN_REQUEST = 5


class TeamMembershipState(Enum[int]):
    INVITED = 1
    ACCEPTED = 2
