from .http import HTTPClient
from .gateway import DiscordGateway
import asyncio
from .channel import GuildChannel

class Client:
    def __init__(self, **kwargs):
        self.session = kwargs.get("session", None)
        self.loop = kwargs.get("loop", None)

        self.http = HTTPClient(loop=self.loop, session=self.session)

        self.shard_id = kwargs.get("shard_id")
        self.ws = None

    async def connect(self, token, *, bot=True, reconnect=True):
        await self.http._login(token, bot=bot)

        params = {
            'initial': True,
            'shard_id': self.shard_id,
        }

        ws = DiscordGateway.client(self, **params)
        self.ws = await asyncio.wait_for(ws, timeout=60.0)

        while True:
            pass

    async def send(self, channel_id, content=None, **kwargs):
        data = await self.http.send_message(channel_id, content, **kwargs)
        return data

    async def fetch_channel(self, channel_id):
        data = await self.http.get_channel(channel_id)
        return data
