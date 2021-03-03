from .bases import BaseObject, BaseState
from .utils import JsonField, Snowflake
from typing import Optional


class PermissionFlag:
    CREATE_INSTANT_INVITE = 0x00000001
    KICK_MEMBERS = 0x00000002
    BAN_MEMBERS = 0x00000004
    ADMINISTRATOR = 0x00000008
    MANAGE_CHANNELS = 0x00000010
    MANAGE_GUILD = 0x00000020
    ADD_REACTIONS = 0x00000040
    VIEW_AUDIT_LOG = 0x00000080
    PRIORITY_SPEAKER = 0x00000100
    STREAM = 0x00000200
    VIEW_CHANNEL = 0x00000400
    SEND_MESSAGES = 0x00000800
    SEND_TTS_MESSAGES = 0x00001000
    MANAGE_MESSAGES = 0x00002000
    EMBED_LINKS = 0x00004000
    ATTACH_FILES = 0x00008000
    READ_MESSAGE_HISTORY = 0x00010000
    MENTION_EVERYONE = 0x00020000
    USE_EXTERNAL_EMOJIS = 0x00040000
    VIEW_GUILD_INSIGHTS = 0x00080000
    CONNECT = 0x00100000
    SPEAK = 0x00200000
    MUTE_MEMBERS = 0x00400000
    DEAFEN_MEMBERS = 0x00800000
    MOVE_MEMBERS = 0x01000000
    USE_VAD = 0x02000000
    CHANGE_NICKNAME = 0x04000000
    MANAGE_NICKNAMES = 0x08000000
    MANAGE_ROLES = 0x10000000
    MANAGE_WEBHOOKS = 0x20000000
    MANAGE_EMOJIS = 0x40000000


class PermissionOverwrite(BaseObject):
    __slots__ = ('id', 'type', 'deny', 'allow')

    __json_fields__ = {
        'allow': JsonField('allow', int, str),
        'deny': JsonField('deny', int, str),
        'type': JsonField('type'),
    }

    id: Snowflake
    allow: int
    deny: int
    type: str

    create_instant_invite: Optional[bool]
    kick_members: Optional[bool]
    ban_members: Optional[bool]
    administrator: Optional[bool]
    manage_channels: Optional[bool]
    manage_guild: Optional[bool]
    add_reactions: Optional[bool]
    view_audit_log: Optional[bool]
    priority_speaker: Optional[bool]
    stream: Optional[bool]
    view_channel: Optional[bool]
    send_messages: Optional[bool]
    send_tts_messages: Optional[bool]
    manage_messages: Optional[bool]
    embed_links: Optional[bool]
    attach_files: Optional[bool]
    read_message_history: Optional[bool]
    mention_everyone: Optional[bool]
    use_external_emojis: Optional[bool]
    view_guild_insights: Optional[bool]
    connect: Optional[bool]
    speak: Optional[bool]
    mute_members: Optional[bool]
    deafen_members: Optional[bool]
    move_members: Optional[bool]
    use_vad: Optional[bool]
    change_nickname: Optional[bool]
    manage_nicknames: Optional[bool]
    manage_roles: Optional[bool]
    manage_webhooks: Optional[bool]
    manage_emojis: Optional[bool]

    def __init__(self, state: 'PermissionOverwriteState'):
        self._state = state

    async def edit(self, overwrite: 'PermissionOverwrite'):
        rest = self._state._client.rest
        await rest.edit_channel_permissions(
            self._state._channel.id,
            self.id, overwrite.allow,
            overwrite.deny,
            overwrite.type
        )

    async def delete(self):
        rest = self._state._client.rest
        await rest.delete_channel_permission(self._state._channel.id, self.id)

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)
        for name, flag in PermissionFlag.__dict__.items():
            if name.startswith('_'):
                continue

            allowed = (flag | self.deny) == flag
            denied = (flag | self.allow) == flag

            if allowed:
                setattr(self, name.lower(), True)
            elif denied:
                setattr(self, name.lower(), False)
            else:
                setattr(self, name.lower(), None)


class PermissionOverwriteState(BaseState):
    __state_class__ = PermissionOverwrite

    def __init__(self, client, channel):
        super().__init__(client)
        self._channel = channel

    def _add(self, data):
        overwrite = self.get(data['id'])
        if overwrite is not None:
            overwrite._update(data)
            return overwrite
        overwrite = self.__state_class__.unmarshal(data, state=self)
        self._values[overwrite.id] = overwrite
        return overwrite
