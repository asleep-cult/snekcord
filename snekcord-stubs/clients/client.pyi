from __future__ import annotations

import asyncio
import signal
import typing as t

from .. import rest
from .. import states
from ..flags import CacheFlags
from ..objects.emojiobject import GuildEmoji
from ..objects.memberobject import GuildMember
from ..objects.messageobject import Message
from ..objects.roleobject import Role
from ..utils.events import EventDispatcher

__all__ = ('ClientClasses', 'Client',)


class ClientClasses:
    RestSession: type[rest.RestSession]
    ChannelState: type[states.ChannelState]
    GuildChannelState: type[states.GuildChannelState]
    GuildEmojiState: type[states.GuildEmojiState]
    GuildBanState: type[states.GuildBanState]
    GuildState: type[states.GuildState]
    IntegrationState: type[states.IntegrationState]
    InviteState: type[states.InviteState]
    GuildMemberState: type[states.GuildMemberState]
    MessageState: type[states.MessageState]
    PermissionOverwriteState: type[states.PermissionOverwriteState]
    ReactionsState: type[states.ReactionsState]
    GuildMemberRoleState: type[states.GuildMemberRoleState]
    RoleState: type[states.RoleState]
    StageInstanceState: type[states.StageInstanceState]
    UserState: type[states.UserState]

    @classmethod
    def set_class(cls, name: str, klass: type) -> None: ...


class Client(EventDispatcher):
    _handled_signals_: t.ClassVar[list[signal.Signals]]

    rest: rest.RestSession
    channels: states.ChannelState
    guilds: states.GuildState
    invites: states.InviteState
    stages: states.StageInstanceState
    users: states.UserState
    finalizing: bool

    def __init__(self, token: str,
                 loop: asyncio.AbstractEventLoop | None = ...,
                 cache_flags: CacheFlags | None = ...,
                 api_version: str = ...) -> None: ...

    @classmethod
    def add_handled_signal(cls, signo: signal.Signals) -> None: ...

    @property
    def members(self) -> t.Generator[GuildMember, None, None]: ...

    @property
    def messages(self) -> t.Generator[Message, None, None]: ...

    @property
    def roles(self) -> t.Generator[Role, None, None]: ...

    @property
    def emojis(self) -> t.Generator[GuildEmoji, None, None]: ...

    async def close(self) -> None: ...

    async def finalize(self) -> None: ...

    async def run_forever(self) -> BaseException | None: ...
