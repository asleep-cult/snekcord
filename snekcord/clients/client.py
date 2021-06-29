import asyncio
import signal

from ..utils.events import EventDispatcher

__all__ = ('ClientClasses', 'Client',)


class _ClientClasses:
    _rest_classes_ = {
        'RestSession',
    }

    _state_classes_ = {
        'ChannelState',
        'GuildChannelState',
        'GuildEmojiState',
        'GuildBanState',
        'GuildState',
        'IntegrationState',
        'InviteState',
        'GuildMemberState',
        'MessageState',
        'PermissionOverwriteState',
        'ReactionsState',
        'GuildMemberRoleState',
        'RoleState',
        'StageInstanceState',
        'UserState',
    }

    _local_classes_ = set()

    def __getattribute__(self, name):
        if name in _ClientClasses._local_classes_:
            return super().__getattribute__(name)
        elif name in _ClientClasses._rest_classes_:
            from .. import rest

            return getattr(rest, name)
        elif name in _ClientClasses._state_classes_:
            from .. import states

            return getattr(states, name)
        else:
            return super().__getattribute__(name)

    def set_class(self, name, klass):
        _ClientClasses._local_classes_.add(name)
        setattr(self, name, klass)


ClientClasses = _ClientClasses()


class Client(EventDispatcher):
    _handled_signals_ = [signal.SIGINT, signal.SIGTERM]

    def __init__(self, token, *, loop=None, cache_flags=None):
        super().__init__(loop=loop)

        self.token = token
        self.cache_flags = cache_flags

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
