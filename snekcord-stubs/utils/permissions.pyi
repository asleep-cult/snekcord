import typing as t

from .bitset import Bitset, Flag

__all__ = ('Permissions',)


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
