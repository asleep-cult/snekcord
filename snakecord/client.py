import asyncio
from typing import Optional

from .channel import ChannelState
from .guild import GuildState
from .user import UserState
from .rest import RestSession
from .invite import InviteState
from .events import EventPusher
from .gateway import Sharder


class Client(EventPusher):
    def __init__(
        self,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        rest: Optional[RestSession] = None,
        channel_state: Optional[ChannelState] = None,
        guild_state: Optional[GuildState] = None,
        user_state: Optional[UserState] = None,
        invite_state: Optional[InviteState] = None,
        sharder: Optional[Sharder] = None,
        max_shards: int = 1
    ):
        super().__init__(loop or asyncio.get_event_loop())

        self.rest = rest or RestSession(client=self)
        self.channels = channel_state or ChannelState(client=self)
        self.guilds = guild_state or GuildState(client=self)
        self.users = user_state or UserState(client=self)
        self.invites = invite_state or InviteState(client=self)
        self.sharder = sharder or Sharder(client=self, max_shards=max_shards)
        self.token: Optional[str] = None

        self.subscribe(self.sharder)

    async def connect(self, token: str):
        self.token = token
        await self.sharder.connect()

    def start(self, token: str):
        self.loop.create_task(self.connect(token))
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            return
