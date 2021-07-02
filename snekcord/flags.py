class Flag:
    def __init__(self, position):
        self.position = position

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return ((instance.value >> self.position) & 1) != 0

    def __set__(self, instance, value):
        if value:
            instance.value |= (1 << self.position)
        else:
            instance.value &= ~(1 << self.position)

    def __delete__(self, instance):
        instance.value &= ~(1 << self.position)


class Bitset:
    def __init__(self, **kwargs):
        self.value = 0
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __init_subclass__(cls):
        cls._length_ = 0
        cls._flags_ = {}

        for name, value in cls.__dict__.items():
            if isinstance(value, Flag):
                cls._flags_[name] = value

                if value.position > cls._length_:
                    cls._length_ = value.position

        cls._length_ += 1

    def __iter__(self):
        for flag in self._flags__:
            yield getattr(self, flag)

    def __index__(self):
        return self.value

    @classmethod
    def all(cls):
        return cls.from_value((1 << cls._length_) - 1)

    @classmethod
    def none(cls):
        return cls.from_value(0)

    @classmethod
    def from_value(cls, value):
        self = cls.__new__(cls)
        self.value = value
        return self

    @classmethod
    def get_value(cls, bitset):
        if isinstance(bitset, int):
            return bitset
        elif isinstance(bitset, Bitset):
            raise bitset.value
        else:
            raise TypeError(f'{bitset!r} is not a valid {cls.__name__}')

    def copy(self):
        return self.from_value(self.value)

    def to_dict(self):
        return dict(zip(self._flags_, self))


class CacheFlags(Bitset):
    guild_bans = Flag(0)
    guild_integrations = Flag(1)
    guild_invites = Flag(2)
    guild_widget = Flag(3)


class WebSocketIntents(Bitset):
    guilds = Flag(0)
    guild_members = Flag(1)
    guild_bans = Flag(2)
    guild_emojis = Flag(3)
    guild_integrations = Flag(4)
    guild_webhooks = Flag(5)
    guild_invites = Flag(6)
    guild_voice_states = Flag(7)
    guild_presences = Flag(8)
    guild_messages = Flag(9)
    guild_message_reactions = Flag(10)
    guild_message_typing = Flag(11)
    direct_messages = Flag(12)
    direct_message_reactions = Flag(13)
    direct_message_typing = Flag(14)


class Permissions(Bitset):
    create_instant_invite = Flag(0)
    kick_members = Flag(1)
    ban_members = Flag(2)
    administrator = Flag(3)
    manage_channels = Flag(4)
    manage_guild = Flag(5)
    add_reactions = Flag(6)
    view_audit_log = Flag(7)
    priority_speaker = Flag(8)
    stream = Flag(9)
    view_channel = Flag(10)
    send_messages = Flag(11)
    send_tts_messages = Flag(12)
    manage_messages = Flag(13)
    embed_links = Flag(14)
    attach_files = Flag(15)
    read_message_history = Flag(16)
    mention_everyone = Flag(17)
    use_external_emojis = Flag(18)
    view_guild_insights = Flag(19)
    connect = Flag(20)
    speak = Flag(21)
    mute_members = Flag(22)
    deafen_members = Flag(23)
    move_members = Flag(24)
    use_vad = Flag(25)
    change_nickname = Flag(26)
    manage_nicknames = Flag(27)
    manage_roles = Flag(28)
    manage_webhoooks = Flag(29)
    manage_emojis = Flag(30)
    use_slash_commands = Flag(31)
    request_to_speak = Flag(32)
    manage_threads = Flag(34)
    use_public_threads = Flag(35)
    use_private_threads = Flag(36)


class SystemChannelFlags(Bitset):
    suppress_join_notifications = Flag(0)
    suppress_premium_subscriptions = Flag(1)
    suppress_guild_reminder_notifications = Flag(2)


class MessageFlags(Bitset):
    crossposted = Flag(0)
    is_crosspost = Flag(1)
    suppress_embeds = Flag(2)
    source_message_deleted = Flag(3)
    urgent = Flag(4)
    has_thread = Flag(5)
    epheneral = Flag(7)
    loading = Flag(8)


class UserFlags(Bitset):
    discord_employee = Flag(0)
    partnered_server_owner = Flag(1)
    hypesquad_events = Flag(2)
    bug_hunter_level_1 = Flag(3)
    mfa_sms = Flag(4)
    premium_promo_dismissed = Flag(5)
    house_bravery = Flag(6)
    house_brilliance = Flag(7)
    house_balance = Flag(8)
    early_supporter = Flag(9)
    team_user = Flag(10)
    has_unread_urgent_message = Flag(13)
    bug_hunter_level_2 = Flag(14)
    verified_bot = Flag(16)
    early_verified_bot_developer = Flag(17)
    discord_certified_moderator = Flag(18)
