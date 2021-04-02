from typing import Optional

from . import structures
from .enums import PermissionFlag
from .state import BaseState


class PermissionOverwrite(structures.PermissionOverwrite):
    __slots__ = ('id', 'type', 'deny', 'allow')

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

    def __init__(self, *, state):
        self._state = state

    async def edit(self, overwrite):
        rest = self._state.client.rest
        await rest.edit_channel_permissions(
            self._state._channel.id,
            self.id, overwrite.allow,
            overwrite.deny,
            overwrite.type
        )

    async def delete(self):
        rest = self._state.client.rest
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
    def __init__(self, *, client, channel):
        super().__init__(client=client)
        self.channel = channel

    def append(self, data):
        overwrite = self.get(data['id'])
        if overwrite is not None:
            overwrite._update(data)
            return overwrite

        overwrite = PermissionOverwrite.unmarshal(data, state=self)
        self._items[overwrite.id] = overwrite
        return overwrite
