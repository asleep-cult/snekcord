import asyncio

from ..auth import Authorization
from ..rest import RESTSession
from ..states import (
    BaseState,
    ChannelState,
    EmojiState,
    GuildState,
    MessageState,
    RoleState,
    UserState,
)

__all__ = ('Client',)


class Client:
    def __init__(self, authorization, *, loop=None):
        if loop is not None:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()

        if isinstance(authorization, Authorization):
            self.authorizaition = authorization
        else:
            self.authorization = Authorization.parse(authorization)

        self.rest = RESTSession(authorization=self.authorization, loop=self.loop)

        self.channels = self.create_channel_state()
        self.guilds = self.create_guild_state()
        self.users = self.create_user_state()

    def enable_events(self, state: BaseState) -> None:
        raise NotImplementedError('This client does not support events.')

    def create_channel_state(self, *, guild=None) -> ChannelState:
        return ChannelState(client=self)

    def create_emoji_state(self, *, guild) -> EmojiState:
        return EmojiState(client=self, guild=guild)

    def create_guild_state(self) -> GuildState:
        return GuildState(client=self)

    def create_member_state(self, *, guild):
        return None

    def create_message_state(self, *, channel) -> MessageState:
        return MessageState(client=self, channel=channel)

    def create_role_state(self, *, guild):
        return RoleState(client=self, guild=guild)

    def create_user_state(self) -> UserState:
        return UserState(client=self)
