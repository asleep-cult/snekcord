import asyncio
import signal

from ..rest import RestSession
from ..states.channelstate import ChannelState, GuildChannelState
from ..states.emojistate import GuildEmojiState
from ..states.guildstate import GuildBanState, GuildState
from ..states.integrationstate import IntegrationState
from ..states.invitestate import InviteState
from ..states.memberstate import GuildMemberState
from ..states.messagestate import MessageState
from ..states.reactionsstate import ReactionsState
from ..states.rolestate import GuildMemberRoleState, RoleState
from ..states.stagestage import StageState
from ..states.userstate import UserState
from ..utils import EventDispatcher

__all__ = ('Client',)


class Client(EventDispatcher):
    DEFAULT_CLASSES = {
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
        'ReactionsState': ReactionsState,
        'GuildMemberRoleState': GuildMemberRoleState,
        'UserState': UserState,
        'StageState': StageState,
        'RestSession': RestSession,
    }

    __classes__ = DEFAULT_CLASSES.copy()
    __handled_signals__ = [signal.SIGINT, signal.SIGTERM]

    def __init__(self, token, *, loop=None, api_version='9'):
        super().__init__(loop=loop)

        self.token = token
        self.api_version = f'v{api_version}'

        self.rest = self.get_class('RestSession')(manager=self)
        self.channels = self.get_class('ChannelState')(manager=self)
        self.guilds = self.get_class('GuildState')(manager=self)
        self.invites = self.get_class('InviteState')(manager=self)
        self.stages = self.get_class('StageState')(manager=self)
        self.users = self.get_class('UserState')(manager=self)

        self.finalizing = False

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

    @property
    def members(self):
        for guild in self.guilds:
            yield from guild.members

    @property
    def messages(self):
        for channel in self.channels:
            yield from channel.messages

    @property
    def roles(self):
        for guild in self.guilds:
            yield from guild.roles

    @property
    def emojis(self):
        for guild in self.guilds:
            yield from guild.emojis

    def _repropagate(self):
        for signo, frame in self._sigpending:
            self._sighandlers[signo](signo, frame)

        self._sigpending.clear()

        for signo in self.__handled_signals__:
            signal.signal(signo, self._sighandlers[signo])

    def _sighandle(self, signo, frame):
        self._sigpending.append((signo, frame))

        if self.finalizing:
            exit()  # give up

        self.finalizing = True

        asyncio.run_coroutine_threadsafe(self.finalize(), loop=self.loop)

    async def close(self):
        await self.rest.aclose()

    async def finalize(self):
        await self.close()

        tasks = asyncio.all_tasks(loop=self.loop)
        for task in tasks:
            if task is not asyncio.current_task() and not task.done():
                task.cancel()

        self.loop.call_soon_threadsafe(self._repropagate)
        self.loop.call_soon_threadsafe(self.loop.close)

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
