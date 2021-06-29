import asyncio
import signal

from ..utils.events import EventDispatcher

__all__ = ('ClientClasses', 'Client',)


class ClientClasses:
    from ..rest import RestSession
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
    from ..states.stagestate import StageInstanceState
    from ..states.userstate import UserState

    @classmethod
    def set_class(cls, name, klass):
        setattr(cls, name, klass)


class Client(EventDispatcher):
    _handled_signals_ = [signal.SIGINT, signal.SIGTERM]

    def __init__(self, token, *, loop=None, cache_flags=None, api_version='9'):
        super().__init__(loop=loop)

        self.token = token
        self.cache_flags = cache_flags
        self.api_version = f'v{api_version}'

        self.rest = ClientClasses.RestSession(client=self)
        self.channels = ClientClasses.ChannelState(client=self)
        self.guilds = ClientClasses.GuildState(client=self)
        self.invites = ClientClasses.InviteState(client=self)
        self.stages = ClientClasses.StageInstanceState(client=self)
        self.users = ClientClasses.UserState(client=self)

        self.finalizing = False

        self._sigpending = []
        self._sighandlers = {}

    @classmethod
    def add_handled_signal(cls, signo):
        cls._handled_signals_.append(signo)

    @property
    def members(self):
        for guild in self.guilds:
            yield from guild.members

    @property
    def messages(self):
        for channel in self.channels:
            if hasattr(channel, 'messages'):
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

        for signo in self._handled_signals_:
            signal.signal(signo, self._sighandlers[signo])

    def _sighandle(self, signo, frame):
        self._sigpending.append((signo, frame))

        if self.finalizing:
            try:
                self._repropagate()
                self.loop.close()
            except BaseException:
                return

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
        for signo in self._handled_signals_:
            self._sighandlers[signo] = signal.getsignal(signo)
            signal.signal(signo, self._sighandle)

        try:
            self.loop.run_forever()
        except BaseException as exc:
            return exc

        return None
