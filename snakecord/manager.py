import asyncio
import signal

from .rest import RestSession
from .states.channelstate import ChannelState, GuildChannelState
from .states.guildstate import GuildBanState, GuildState
from .states.invitestate import InviteState
from .states.memberstate import GuildMemberState
from .states.rolestate import GuildMemberRoleState, RoleState
from .states.userstate import UserState

HANDLED_SIGNALS = []

for signo in ('SIGINT', 'SIGTERM'):
    signo = getattr(signal, signo, None)
    if signo is not None:
        HANDLED_SIGNALS.append(signo)

default_states = {
    klass.__name__: klass
    for klass in (ChannelState, GuildChannelState, GuildState,
                  GuildBanState, InviteState, RoleState, GuildMemberState,
                  GuildMemberRoleState, UserState, RestSession)
}


class BaseManager:
    __classes__ = default_states

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
        self._old_handlers = {}

    @classmethod
    def set_class(cls, name, klass):
        default = default_states[name]
        assert issubclass(klass, default)
        cls.__classes__[name] = klass

    @classmethod
    def get_class(cls, name):
        return cls.__classes__[name]

    def _repropagate(self, signo, frame):
        old_handler = self._old_handlers[signo]
        old_handler(signo, frame)

        try:
            signal.signal(signo, old_handler)
        except BaseException:
            pass

    def _sighandle(self, signo, frame):
        if self.closing:
            return

        self.closing = True

        try:
            signal.signal(signo, lambda *args: None)
        except BaseException:
            pass

        task = self.loop.create_task(self.rest.aclose())
        task.add_done_callback(
            lambda future: self._repropagate(signo, frame))

    def run_forever(self):
        for signo in HANDLED_SIGNALS:
            try:
                self._old_handlers[signo] = signal.getsignal(signo)
                signal.signal(signo, self._sighandle)
            except BaseException:
                pass

        self.loop.run_forever()
