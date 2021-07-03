import asyncio
import signal
import weakref

__all__ = ('ClientClasses', 'Client',)


class _ClientClasses:
    _object_classes_ = {
        'GuildChannel',
        'FollowedChannel',
        'TextChannel',
        'CategoryChannel',
        'VoiceChannel',
        'DMChannel',
        'GuildEmoji',
        'PartialGuildEmoji',
        'UnicodeEmoji',
        'PartialUnicodeEmoji',
        'Guild',
        'Integration',
        'Invite',
        'GuildVanityURL',
        'GuildMember',
        'Message',
        'PermissionOverwrite',
        'Reactions',
        'Role',
        'StageInstance',
        'GuildTemplate',
        'User',
        'GuildWidget',
        'WelcomeScreen',
    }

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
        'ChannelPinsState',
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
        elif name in _ClientClasses._object_classes_:
            from .. import objects

            return getattr(objects, name)
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


class _EventWaiter:
    def __init__(self, name, client, timeout, filter):
        self.name = name
        self.client = client
        self.timeout = timeout
        self.filter = filter
        self._queue = asyncio.Queue()

    def _put(self, args):
        if self.filter is not None:
            if not self.filter(*args):
                return

        self._queue.put_nowait(args)

    async def _get(self):
        coro = self._queue.get()
        args = await asyncio.wait_for(coro, timeout=self.timeout)

        if len(args) == 1:
            return args[0]
        else:
            return args

    def __await__(self):
        return self._get().__await__()

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self._get()

    def __del__(self):
        try:
            self.client.remove_waiter(self)
        except KeyError:
            pass


class Client:
    _events_ = None

    _handled_signals_ = [signal.SIGINT, signal.SIGTERM]

    def __init__(self, token, *, loop=None, cache_flags=None):
        if loop is not None:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()

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

        self._listeners = {}
        self._waiters = {}

    @classmethod
    def add_handled_signal(cls, signo):
        cls._handled_signals_.append(signo)

    def itermembers(self):
        for guild in self.guilds:
            yield from guild.members

    def iteremojis(self):
        for guild in self.guilds:
            yield from guild.emojis

    def register_listener(self, name, callback, *, persistent=True):
        name = name.lower()

        listeners = self._listeners.get(name.lower())
        if listeners is None:
            listeners = self._listeners[name] = []

        listeners.append((callback, persistent))

    def remove_listener(self, name, callback):
        listeners = self._listeners.get(name.lower())
        for i, (listener, _) in enumerate(listeners):
            if listener is callback:
                listeners.pop(i)

    def register_waiter(self, name, *, timeout=None, filter=None):
        name = name.lower()
        waiter = _EventWaiter(name, self, timeout, filter)

        waiters = self._waiters.get(name)
        if waiters is None:
            waiters = self._waiters[name] = weakref.WeakSet()

        waiters.add(waiter)

        return waiter

    wait = register_waiter

    def remove_waiter(self, waiter):
        waiters = self._waiters.get(waiter.name)
        if waiters is not None:
            waiters.remove(waiter)

    def run_callbacks(self, name, *args):
        name = name.lower()

        listeners = self._listeners.get(name)
        waiters = self._waiters.get(name)

        if listeners is not None:
            for listener, persistent in listeners:
                ret = listener(*args)
                if asyncio.iscoroutinefunction(listener):
                    self.loop.create_task(ret)

                if not persistent:
                    listeners.remove((listener, persistent))

        if waiters is not None:
            for waiter in tuple(waiters):
                waiter._put(args)

    async def dispatch(self, name, *args):
        if self._events_ is not None:
            event = self._events_.get(name.lower())

            if event is not None:
                evt = await event(self, *args)
                args = (evt,)

        self.run_callbacks(name, *args)

    def on(self, name=None):
        def wrapped(func):
            self.register_listener(name or func.__name__, func)
            return func
        return wrapped

    def once(self, name=None):
        def wrapped(func):
            self.register_listener(name or func.__name__, func, persistent=False)
            return func
        return wrapped

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
