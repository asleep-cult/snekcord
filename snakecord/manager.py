import asyncio
import signal

from .rest import RestSession
from .states.channelstate import ChannelState, GuildChannelState
from .states.guildstate import GuildBanState, GuildState
from .states.invitestate import InviteState
from .states.memberstate import GuildMemberState
from .states.messagestate import MessageState
from .states.rolestate import GuildMemberRoleState, RoleState
from .states.userstate import UserState


class BaseManager:
    DEFAULT_CLASSES = {
        'ChannelState': ChannelState,
        'GuildChannelState': GuildChannelState,
        'GuildState': GuildState,
        'GuildBanState': GuildBanState,
        'InviteState': InviteState,
        'RoleState': RoleState,
        'GuildMemberState': GuildMemberState,
        'MessageState': MessageState,
        'GuildMemberRoleState': GuildMemberRoleState,
        'UserState': UserState,
        'RestSession': RestSession,
    }

    __classes__ = DEFAULT_CLASSES.copy()
    __handled_signals__ = [signal.SIGINT, signal.SIGTERM]

    def __init__(self, token, *, loop=None, api_version='9'):
        if loop is not None:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()

        self.token = token
        self.api_version = f'v{api_version}'

        self.rest = self.get_class('RestSession')(manager=self)
        self.channels = self.get_class('ChannelState')(manager=self)
        self.guilds = self.get_class('GuildState')(manager=self)
        self.invites = self.get_class('InviteState')(manager=self)
        self.users = self.get_class('UserState')(manager=self)

        self.closing = False
        self.finalized = False

        self._sigpending = []
        self._sighandlers = {}

    @classmethod
    def set_class(cls, name, klass):
        default = cls.DEFAULT_CLASSES[name]
        assert issubclass(klass, default)
        cls.__classes__[name] = klass

    @classmethod
    def get_class(cls, name):
        return cls.__classes__[name]

    @classmethod
    def add_handled_signal(cls, signo):
        cls.__handled_signals__.append(signo)

    def _repropagate(self):
        for signo, frame in self._sigpending:
            self._sighandlers[signo](signo, frame)

        self._sigpending.clear()

        for signo in self.__handled_signals__:
            signal.signal(signo, self._sighandlers[signo])

    def _sighandle(self, signo, frame):
        self._sigpending.append((signo, frame))

        if self.closing:
            return

        self.closing = True

        asyncio.run_coroutine_threadsafe(self.finalize(), loop=self.loop)

    async def close(self):
        await self.rest.aclose()

    async def finalize(self):
        if self.finalized:
            return

        self.finalized = True

        await self.close()

        tasks = asyncio.all_tasks(loop=self.loop)
        for task in tasks:
            if task is not asyncio.current_task() and not task.done():
                task.cancel()

        self.loop.call_soon_threadsafe(self._repropagate)
        self.loop.call_soon_threadsafe(self.loop.stop)

    def run_forever(self):
        for signo in self.__handled_signals__:
            try:
                self._sighandlers[signo] = signal.getsignal(signo)
                signal.signal(signo, self._sighandle)
            except BaseException:
                pass

        try:
            self.loop.run_forever()
        except BaseException as exc:
            return exc
