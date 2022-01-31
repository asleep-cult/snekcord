from __future__ import annotations

import typing

from ..auth import Authorization
from ..rest import RESTSession
from ..states import (
    ChannelMessagesView,
    ChannelState,
    EmojiState,
    EventState,
    GuildChannelsView,
    GuildEmojisView,
    GuildRolesView,
    GuildState,
    InviteState,
    MessageState,
    RoleState,
    SupportsChannelID,
    SupportsEmojiID,
    SupportsGuildID,
    SupportsMessageID,
    SupportsRoleID,
    UserState,
)

__all__ = ('Client',)


class Client:
    def __init__(self, authorization: typing.Union[Authorization, str]) -> None:
        if isinstance(authorization, Authorization):
            self.authorization = authorization
        else:
            self.authorization = Authorization.parse(authorization)

        self.events: typing.Dict[str, EventState[typing.Any, typing.Any]] = {}

        self.rest = RESTSession(authorization=self.authorization)

        self.channels = self.create_channel_state()
        self.emojis = self.create_emoji_state()
        self.guilds = self.create_guild_state()
        self.invites = self.create_invite_state()
        self.messages = self.create_message_state()
        self.roles = self.create_role_state()
        self.users = self.create_user_state()

    def create_channel_state(self) -> ChannelState:
        return ChannelState(client=self)

    def create_emoji_state(self) -> EmojiState:
        return EmojiState(client=self)

    def create_guild_state(self) -> GuildState:
        return GuildState(client=self)

    def create_invite_state(self) -> InviteState:
        return InviteState(client=self)

    def create_message_state(self) -> MessageState:
        return MessageState(client=self)

    def create_role_state(self) -> RoleState:
        return RoleState(client=self)

    def create_user_state(self) -> UserState:
        return UserState(client=self)

    def create_channel_messages_view(
        self, messages: typing.Iterable[SupportsMessageID], channel: SupportsChannelID
    ) -> ChannelMessagesView:
        return ChannelMessagesView(state=self.messages, messages=messages, channel=channel)

    def create_guild_channels_view(
        self, channels: typing.Iterable[SupportsChannelID], guild: SupportsGuildID
    ) -> GuildChannelsView:
        return GuildChannelsView(state=self.channels, channels=channels, guild=guild)

    def create_guild_emojis_view(
        self, emojis: typing.Iterable[SupportsEmojiID], guild: SupportsGuildID
    ) -> GuildEmojisView:
        return GuildEmojisView(state=self.emojis, emojis=emojis, guild=guild)

    def create_guild_roles_view(
        self, roles: typing.Iterable[SupportsRoleID], guild: SupportsGuildID
    ) -> GuildRolesView:
        return GuildRolesView(state=self.roles, roles=roles, guild=guild)
