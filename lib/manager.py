import asyncio

from .rest import RestSession
from .guild import Guild
from .shard import (
    Shard, 
    DiscordResponse
)

from typing import (
    Dict,
    Callable,
    Any
)

class Manager:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.token: str = None
        self.loop = loop
        self.intents = 0
        self.rest = RestSession(self)
        self.ws = Shard(self)
        self.events: Dict[str, Callable] = {}
        self._guilds: Dict[str, Guild] = {}
        self._channels = {}

    def register_event(self, func: Callable) -> None:
        name = func.__name__.lower()
        try:
            self.events[name].append(func)
        except KeyError:
            self.events[name] = [func]

    def ready(self, data) -> None:
        self.call_events('ready')

    def guild_create(self, data: Dict[str, Any]) -> None:
        guild = Guild.unmarshal(data, manager=self)
        self._guilds[guild.id] = guild
        self.call_events('guild_create', guild)

    def dispatch(self, resp: DiscordResponse) -> None:
        name = resp.event_name.lower()
        func = getattr(self, name, None)
        if func is not None:
            func(resp.data)

    def call_events(self, name: str, *args, **kwargs) -> None:
        for event in self.events.get(name, []):
            self.loop.create_task(event(*args, **kwargs))

    def start(self, token: str) -> None:
        self.token = token
        self.loop.create_task(self.ws.connect())
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            return