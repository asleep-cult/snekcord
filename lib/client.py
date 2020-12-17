import asyncio
from .manager import Manager

class Client:
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.manager = Manager(self.loop)

    def get_guild(self, guild_id: str):
        return self.manager._guilds.get(guild_id)

    def on(self, func):
        self.manager.register_event(func)

    def start(self, token):
        self.manager.start(token)
 
class Bot(Client):
    pass

class Mudkip(Client):
    cool = True
