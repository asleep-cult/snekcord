from __future__ import annotations

from typing import Union

from ..auth import Authorization
from ..rest import RESTSession
from ..states import (
    BaseClientState,
    ChannelMessageState,
    ChannelState,
    EmojiState,
    GuildChannelState,
    GuildRoleState,
    GuildState,
    InviteState,
    MessageState,
    RoleState,
    UserState,
)

__all__ = ('Client',)


class Client:
    def __init__(self, authorization: Union[Authorization, str]) -> None:
        if isinstance(authorization, Authorization):
            self.authorization = authorization
        else:
            self.authorization = Authorization.parse(authorization)

        self.rest = RESTSession(authorization=self.authorization)

        self.channels = self.create_channel_state()
        self.guilds = self.create_guild_state()
        self.invites = self.create_invite_state()
        self.messages = self.create_message_state()
        self.roles = self.create_role_state()
        self.users = self.create_user_state()

    def enable_events(self, state: BaseClientState, *, implicit: bool = False) -> None:
        raise NotImplementedError('This client does not support events.')

    def create_channel_state(self, *, guild=None) -> Union[GuildChannelState, ChannelState]:
        if guild is not None:
            return GuildChannelState(superstate=self.channels, guild=guild)
        else:
            return ChannelState(client=self)

    def create_emoji_state(self, *, guild) -> EmojiState:
        return EmojiState(client=self, guild=guild)

    def create_guild_state(self) -> GuildState:
        return GuildState(client=self)

    def create_invite_state(self) -> InviteState:
        return InviteState(client=self)

    def create_member_state(self, *, guild):
        return None

    def create_message_state(self, *, channel=None) -> Union[ChannelMessageState, MessageState]:
        if channel is not None:
            return ChannelMessageState(superstate=self.messages, channel=channel)
        else:
            return MessageState(client=self)

    def create_role_state(self, *, guild=None) -> Union[GuildRoleState, RoleState]:
        if guild is not None:
            return GuildRoleState(superstate=self.roles, guild=guild)
        else:
            return RoleState(client=self)

    def create_user_state(self) -> UserState:
        return UserState(client=self)
