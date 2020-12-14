from .client import Client
import sys
import json
import aiohttp

class DiscordGateway:
    def __init__(self, socket : aiohttp.ClientWebSocketResponse) -> None:
        self.socket = socket

    @classmethod
    async def client(cls, client : Client, *, shard_id=None, session=None, sequence=None, resume=False):
        gateway = await client.http.gateway()
        socket = await client.http.websocket_connect(gateway)

        ws = cls(socket)

        ws.token = client.http.token
        ws.gateway = gateway
        ws.shard_id = shard_id
        ws.session = session
        ws.sequence = sequence

        if not resume:
            await ws.identify()
            return ws

        await ws.resume()
        return ws

    async def identify(self):
        payload = {
            'op': 2,
            'd' : {
                'token': self.token,
                "intents": 513,
                'properties': {
                    '$os': sys.platform,
                    '$browser': 'py-discord-api',
                    '$library': 'py-discord-api'
                },
                'compress': True,
                'large_threshold': 250,
            }
        }
        await self.send(payload)

    async def resume(self):
        payload = {
            'op': 6,
            'd': {
                'seq': self.sequence,
                'session_id': self.session_id,
                'token': self.token
            }
        }
        await self.send(payload)

    async def send(self, data):
        obj = json.dumps(data, separators=(',', ':'), ensure_ascii=True)
        await self.socket.send_str(obj)
