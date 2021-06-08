from __future__ import annotations

import asyncio
import signal
from types import FrameType
import typing as t

from ..rest import RestSession
from ..states.basestate import BaseState
from ..states.channelstate import ChannelState, GuildChannelState
from ..states.emojistate import GuildEmojiState
from ..states.guildstate import GuildBanState, GuildState
from ..states.integrationstate import IntegrationState
from ..states.invitestate import InviteState
from ..states.memberstate import GuildMemberState
from ..states.messagestate import MessageState
from ..states.overwritestate import PermissionOverwriteState
from ..states.reactionsstate import ReactionsState
from ..states.rolestate import GuildMemberRoleState, RoleState
from ..states.stagestage import StageState
from ..states.userstate import UserState
from ..utils import Bitset, EventDispatcher, Flag

__all__ = ('CacheFlags', 'Client')

if t.TYPE_CHECKING:
    from signal import Signals

    from ..objects import BaseObject, GuildMember, GuildEmoji, Message, Role


class CacheFlags(Bitset):
    guild_bans = Flag(0)
    guild_integrations = Flag(1)
    guild_invites = Flag(2)
    guild_widget = Flag(3)


class Client(EventDispatcher):
    DEFAULT_CLASSES: t.Dict[
        str, t.Type[t.Union[BaseState[t.Any, BaseObject], RestSession]]
    ] = {
        'ChannelState': ChannelState,
        'GuildChannelState': GuildChannelState,
        'GuildEmojiState': GuildEmojiState,
        'GuildState': GuildState,
        'IntegrationState': IntegrationState,
        'GuildBanState': GuildBanState,
        'InviteState': InviteState,
        'RoleState': RoleState,
        'GuildMemberState': GuildMemberState,
        'MessageState': MessageState,
        'PermissionOverwriteState': PermissionOverwriteState,
        'ReactionsState': ReactionsState,
        'GuildMemberRoleState': GuildMemberRoleState,
        'UserState': UserState,
        'StageState': StageState,
        'RestSession': RestSession,
    }  # type: ignore

    if t.TYPE_CHECKING:
        rest: RestSession
        channels: ChannelState
        guilds: GuildState
        invites: InviteState
        stages: StageState
        users: UserState
        finalizing: bool

    __classes__ = DEFAULT_CLASSES.copy()
    __handled_signals__ = [signal.SIGINT, signal.SIGTERM]

    def __init__(self, token: str, *,
                 loop: t.Optional[asyncio.AbstractEventLoop] = None,
                 cache_flags: t.Optional[CacheFlags] = None,
                 api_version: str = '9'
                 ) -> None:
        super().__init__(loop=loop)

        self.token = token
        self.cache_flags = cache_flags
        self.api_version = f'v{api_version}'

        self.rest = self.get_class('RestSession')(client=self)
        self.channels = self.get_class('ChannelState')(client=self)
        self.guilds = self.get_class('GuildState')(client=self)
        self.invites = self.get_class('InviteState')(client=self)
        self.stages = self.get_class('StageState')(client=self)
        self.users = self.get_class('UserState')(client=self)

        self.finalizing = False

        self._sigpending = []
        self._sighandlers = {}

    @classmethod
    def set_class(cls, name: str, klass: type) -> None:
        default = cls.DEFAULT_CLASSES[name]
        assert issubclass(klass, default)  # type: ignore
        cls.__classes__[name] = klass

    @classmethod
    def get_class(
        cls, name: str
    ) -> t.Type[t.Union[BaseState[t.Any, BaseObject], RestSession]]:
        return cls.__classes__[name]

    @classmethod
    def add_handled_signal(cls, signo: Signals) -> None:
        cls.__handled_signals__.append(signo)

    @property
    def members(self) -> t.Generator[GuildMember, None, None]:
        for guild in self.guilds:
            yield from guild.members

    @property
    def messages(self) -> t.Generator[Message, None, None]:
        for channel in self.channels:
            yield from channel.messages

    @property
    def roles(self) -> t.Generator[Role, None, None]:
        for guild in self.guilds:
            yield from guild.roles

    @property
    def emojis(self) -> t.Generator[GuildEmoji, None, None]:
        for guild in self.guilds:
            yield from guild.emojis

    def _repropagate(self) -> None:
        for signo, frame in self._sigpending:
            self._sighandlers[signo](signo, frame)

        self._sigpending.clear()

        for signo in self.__handled_signals__:
            signal.signal(signo, self._sighandlers[signo])

    def _sighandle(self, signo: int, frame: FrameType) -> None:
        self._sigpending.append((signo, frame))

        if self.finalizing:
            try:
                self._repropagate()
                self.loop.close()
            except BaseException:
                return

        self.finalizing = True

        asyncio.run_coroutine_threadsafe(self.finalize(), loop=self.loop)

    async def close(self) -> None:
        await self.rest.aclose()

    async def finalize(self) -> None:
        await self.close()

        tasks = asyncio.all_tasks(loop=self.loop)
        for task in tasks:
            if task is not asyncio.current_task() and not task.done():
                task.cancel()

        self.loop.call_soon_threadsafe(self._repropagate)
        self.loop.call_soon_threadsafe(self.loop.close)

    def run_forever(self) -> t.Optional[BaseException]:
        for signo in self.__handled_signals__:
            try:
                self._sighandlers[signo] = (  # type: ignore
                    signal.getsignal(signo))

                signal.signal(signo, self._sighandle)
            except BaseException:
                pass

        try:
            self.loop.run_forever()
        except BaseException as exc:
            return exc
