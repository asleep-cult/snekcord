from __future__ import annotations

import typing as t

T = t.TypeVar('T')


class Flag:
    position: int

    def __init__(self, position: int) -> None: ...

    @t.overload
    def __get__(self, instance: None, owner: type[Bitset]) -> Flag:
        ...

    @t.overload
    def __get__(self, instance: Bitset, owner: type[Bitset]) -> bool:
        ...


class Bitset:
    _length_: t.ClassVar[int]
    _flags_: t.ClassVar[dict[str, Flag]]

    def __init__(self, **kwargs: bool) -> None: ...

    def __iter__(self) -> t.Generator[bool, None, None]: ...

    @classmethod
    def all(cls: type[T]) -> T: ...

    @classmethod
    def none(cls: type[T]) -> T: ...

    @classmethod
    def from_value(cls: type[T], value: int) -> T: ...

    def to_dict(self) -> dict[str, bool]: ...


class CacheFlags(Bitset):
    guild_bans: t.ClassVar[Flag]
    guild_integrations: t.ClassVar[Flag]
    guild_invites: t.ClassVar[Flag]
    guild_widget: t.ClassVar[Flag]


class WebSocketIntents(Bitset):
    guilds: t.ClassVar[Flag]
    guild_members: t.ClassVar[Flag]
    guild_bans: t.ClassVar[Flag]
    guild_emojis: t.ClassVar[Flag]
    guild_integrations: t.ClassVar[Flag]
    guild_webhooks: t.ClassVar[Flag]
    guild_invites: t.ClassVar[Flag]
    guild_voice_states: t.ClassVar[Flag]
    guild_presences: t.ClassVar[Flag]
    guild_messages: t.ClassVar[Flag]
    guild_message_reactions: t.ClassVar[Flag]
    guild_message_typing: t.ClassVar[Flag]
    direct_messages: t.ClassVar[Flag]
    direct_message_reactions: t.ClassVar[Flag]
    direct_message_typing: t.ClassVar[Flag]


class Permissions(Bitset):
    create_instant_invite: t.ClassVar[Flag]
    kick_members: t.ClassVar[Flag]
    ban_members: t.ClassVar[Flag]
    administrator: t.ClassVar[Flag]
    manage_channels: t.ClassVar[Flag]
    manage_guild: t.ClassVar[Flag]
    add_reactions: t.ClassVar[Flag]
    view_audit_log: t.ClassVar[Flag]
    priority_speaker: t.ClassVar[Flag]
    stream: t.ClassVar[Flag]
    view_channel: t.ClassVar[Flag]
    send_messages: t.ClassVar[Flag]
    send_tts_messages: t.ClassVar[Flag]
    manage_messages: t.ClassVar[Flag]
    embed_links: t.ClassVar[Flag]
    attach_files: t.ClassVar[Flag]
    read_message_history: t.ClassVar[Flag]
    mention_everyone: t.ClassVar[Flag]
    use_external_emojis: t.ClassVar[Flag]
    view_guild_insights: t.ClassVar[Flag]
    connect: t.ClassVar[Flag]
    speak: t.ClassVar[Flag]
    mute_members: t.ClassVar[Flag]
    deafen_members: t.ClassVar[Flag]
    move_members: t.ClassVar[Flag]
    use_vad: t.ClassVar[Flag]
    change_nickname: t.ClassVar[Flag]
    manage_nicknames: t.ClassVar[Flag]
    manage_roles: t.ClassVar[Flag]
    manage_webhoooks: t.ClassVar[Flag]
    manage_emojis: t.ClassVar[Flag]
    use_slash_commands: t.ClassVar[Flag]
    request_to_speak: t.ClassVar[Flag]
    manage_threads: t.ClassVar[Flag]
    use_public_threads: t.ClassVar[Flag]
    use_private_threads: t.ClassVar[Flag]


class SystemChannelFlags(Bitset):
    suppress_join_notifications: t.ClassVar[Flag]
    suppress_premium_subscriptions: t.ClassVar[Flag]
    suppress_guild_reminder_notifications: t.ClassVar[Flag]


class MessageFlags(Bitset):
    crossposted: t.ClassVar[Flag]
    is_crosspost: t.ClassVar[Flag]
    suppress_embeds: t.ClassVar[Flag]
    source_message_deleted: t.ClassVar[Flag]
    urgent: t.ClassVar[Flag]
    has_thread: t.ClassVar[Flag]
    ephemeral: t.ClassVar[Flag]
    loading: t.ClassVar[Flag]


class UserFlags(Bitset):
    discord_employee: t.ClassVar[Flag]
    partnered_server_owner: t.ClassVar[Flag]
    hypesquad_events: t.ClassVar[Flag]
    bug_hunter_level_1: t.ClassVar[Flag]
    mfa_sms: t.ClassVar[Flag]
    premium_promo_dismissed: t.ClassVar[Flag]
    house_bravery: t.ClassVar[Flag]
    house_brilliance: t.ClassVar[Flag]
    house_balance: t.ClassVar[Flag]
    early_supporter: t.ClassVar[Flag]
    team_user: t.ClassVar[Flag]
    has_unread_urgent_message: t.ClassVar[Flag]
    bug_hunter_level_2: t.ClassVar[Flag]
    verified_bot: t.ClassVar[Flag]
    early_verified_bot_developer: t.ClassVar[Flag]
    discord_certified_moderator: t.ClassVar[Flag]
