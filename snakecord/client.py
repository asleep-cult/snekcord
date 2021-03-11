import asyncio
from .channel import ChannelState
from .guild import GuildState
from .user import UserState
from .rest import RestSession
from .invite import InviteState
from .events import EventPusher
from .gateway import Sharder


class Client:
    def __init__(
        self,
        loop=None,
        rest=None,
        channel_state=None,
        guild_state=None,
        user_state=None,
        invite_state=None,
        sharder=None,
        max_shards=1
    ):
        self.loop = loop or asyncio.get_event_loop()
        self.rest = rest or RestSession(self)
        self.channels = channel_state or ChannelState(self)
        self.guilds = guild_state or GuildState(self)
        self.users = user_state or UserState(self)
        self.invites = invite_state or InviteState(self)
        self.events = self.sharder = sharder or Sharder(self, max_shards=max_shards)
        self.token = None

    def start(self, token):
        self.token = token
        self.loop.create_task(self.sharder.connect())
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            return
