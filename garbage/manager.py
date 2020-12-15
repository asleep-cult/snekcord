import asyncio
import typing as t
from .guild import Guild
from . import shard

class Manager:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.token: str = None
        self.loop = loop
        self.intents = 0
        self.ws = shard.Shard(self, self.loop)
        self.events = {}
        self._guilds: t.Dict[str, Guild] = {}

    def register_event(self, func):
        name = func.__name__.lower()
        try:
            self.events[name].append(func)
        except KeyError:
            self.events[name] = [func]

    def guild_create(self, data: t.Dict[str, t.Any]) -> Guild:
        guild = Guild(manager=self, data=data)
        self._guilds[guild.id] = guild
        return (guild), {}

    def dispatch(self, resp: shard.DiscordResponse):
        name = resp.event_name.lower()
        print(name)
        print(self.events)
        func = getattr(self, name)
        args, kwargs = func(resp.data)
        for event in self.events.get(name, []):
            self.loop.create_task(event(*args, **kwargs))

    def start(self, token):
        self.token = token
        self.loop.create_task(self.ws.connect())
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            return