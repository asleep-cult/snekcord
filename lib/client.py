import asyncio
from .channel import ChannelState
from .guild import GuildState
from .rest import RestSession
from .events import EventHandler
from .gateway import Gateway

class Client:
    def __init__(self, loop=None, rest=None, channel_state=None, guild_state=None, event_handler=None, ws=None, sharded=False):
        self.loop = loop or asyncio.get_event_loop()
        self.rest = rest or RestSession(self)
        self.channels = channel_state or ChannelState(self)
        self.guilds = guild_state or GuildState(self)
        self.events = event_handler or EventHandler(self)
        self.ws = ws or Gateway(self, sharded)
        self.token = None

    def on(self, func):
        return self.events.add_listener(func)

    def start(self, token):
        self.token = token
        self.loop.create_task(self.ws.connect())
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            return