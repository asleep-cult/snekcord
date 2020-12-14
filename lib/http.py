import aiohttp
import asyncio
from urllib.parse import quote
from .channel import DMChannel, TextChannel, VoiceChannel


class Base:
    def __init__(self, method, route : str, **parameters) -> None:
        self.BASE = 'https://discord.com/api/v7'
        url = self.BASE + route

        self.method = method

        if parameters:
            self.url = url.format(**{k: quote(v) if isinstance(v, str) else v for k, v in parameters.items()})

        self.guild_id = parameters.get("guild_id")
        self.channel_id = parameters.get("channel_id")
        self.user_id = parameters.get("user_id")


class HTTPClient:
    def __init__(self, *, loop=None, session=None) -> None:
        self.token = None
        self.bot_token = True

        self.loop = loop or asyncio.get_event_loop()
        self._session = session or aiohttp.ClientSession(loop=self.loop)

    async def websocket_connect(self, url : str):
        kwargs = {
            'max_msg_size': 0,
            'timeout': 30.0,
            'autoclose': False,
            'compress': 0
        }

        return await self._session.ws_connect(url, **kwargs)

    async def request(self, route : Base, **kwargs):
        method = route.method
        url = route.url

        headers = {
            'Authorization': 'Bot ' + self.token
        }

        kwargs["headers"] = headers

        async with self._session.request(method, url, **kwargs) as response:
            if 300 > response.status >= 200:

                data = await response.json()
                return data

    async def gateway(self, *, encoding='json', v=6):
        data = await self.request(Base('GET', '/gateway'))
        value = '{0}?encoding={1}&v={2}'

        return value.format(data['url'], encoding, v)

    def _token(self, token , *, bot=True):
        self.token = token
        self.bot_token = bot

    async def _login(self, token, *, bot=True):
        self._token(token, bot=bot)

        data = await self.request(Base('GET', '/users/@me'))
        return data

    async def close(self):
        await self._session.close()

    async def send_message(self, channel_id, content=None, *, tts=False, embed=None):
        route = Base('POST', '/channels/{channel_id}/messages', channel_id=channel_id)
        payload = {}

        if content:
            payload['content'] = content

        if tts:
            payload['tts'] = True

        if embed:
            payload['embed'] = embed

        return await self.request(route, json=payload)

    async def get_message(self, channel_id, message_id):
        route = Base('GET', '/channels/{channel_id}/messages/{message_id}', channel_id=channel_id, message_id=message_id)
        return await self.request(route)

    async def kick(self, user_id, guild_id, *, reason:str=None):
        route = Base("DELETE", '/guilds/{guild_id}/members/{user_id}', guild_id=guild_id, user_id=user_id)
        
        if reason:
            route.url =' {0.url}?reason={1}'.format(route, reason)

        return await self.request(route)

    async def ban(self, guild_id, user_id, *, reason:str=None, deleted_message_days=14):
        route = Base('PUT', '/guilds/{guild_id}/bans/{user_id}', guild_id=guild_id, user_id=user_id)
        kwargs = {
            "delete_message_days": deleted_message_days
        }
        if reason:
            route.url = '{0.url}?reason={1}'.format(route, reason)

        return await self.request(route, params=kwargs)

    async def unban(self, guild_id, user_id, *, reason=None):
        route = Base("DELETE", '/guilds/{guild_id}/bans/{user_id}', guild_id=guild_id, user_id=user_id)
        return await self.request(route, reason=reason)

    async def get_guild_member(self, guild_id, user_id):
        route = Base("GET", '/guilds/{guild_id}/members/{user_id}', guild_id=guild_id, user_id=user_id)
        return await self.request(route)

    async def get_channel(self, channel_id):
        route = Base('GET', '/channels/{channel_id}', channel_id=channel_id)
        data = await self.request(route)

        if data['type'] == 0:
            return TextChannel(data)

        if data['type'] == 2:
            return VoiceChannel(data)

        if data['type'] == 1:
            return DMChannel(data)

    async def delete_channel(self, channel_id):
        route = Base('DELETE', '/channels/{channel_id}', channel_id=channel_id)
        return await self.request(route)

    async def edit_channel(self, channel_id, *, reason=None, **options):
        route = Base('PATCH', '/channels/{channel_id}', channel_id=channel_id)

        valid_options = ('name', 'parent_id', 'topic',
                         'bitrate', 'nsfw','user_limit',
                         'position', 'permission_overwrites', 'rate_limit_per_user',
                        'type')
        payload = {
            key: value for key, value in options.items() if key in valid_options
        }

        return await self.request(route, reason=reason, json=payload)

    async def get_guild(self, guild_id, *, with_counts=False):
        r_url = '/guilds/{guild_id}'

        if with_counts:
            r_url = '/guilds/{guild_id}?with_counts=True'

        route = Base('GET', r_url, guild_id=guild_id)
        return await self.request(route)

    async def delete_guild(self, guild_id):
        route = Base("DELETE", "/guilds/{guild_id}", guild_id=guild_id)
        return await self.request(route)

    async def create_guild_role(self, guild_id, *, name:str=None, permissions=None,
                                color=None, hoist:bool=None,
                                mentionable:bool=None):

        route = Base("POST", "/guilds/{guild_id}/roles", guild_id=guild_id)

        payload = {
            'name': str(name),
            'permissions': permissions,
            'color': color,
            'hoist': hoist,
            'mentionable': mentionable
        }
        return await self.request(route, json=payload)

    async def delete_guild_role(self, guild_id, role_id):
        route = Base('DELETE', "/guilds/{guild_id}/roles/{role_id}", guild_id=guild_id, role_id=role_id)
        return await self.request(route)

    async def add_member_role(self, guild_id, user_id, role_id):
        route = Base('PUT', '/guilds/{guild_id}/members/{user_id}/roles/{role_id}', guild_id=guild_id, user_id=user_id, role_id=role_id)
        return await self.request(route)

    async def remove_member_role(self, guild_id, user_id, role_id):
        route = Base('DELETE', '/guilds/{guild_id}/members/{user_id}/roles/{role_id}', guild_id=guild_id, user_id=user_id, role_id=role_id)
        return await self.request(route)

    async def get_guild_bans(self, guild_id):
        route = Base('GET', '/guilds/{guild_id}/bans', guild_id=guild_id)
        return await self.request(route)

    async def get_guild_ban(self, guild_id, user_id):
        route = Base('GET', '/guilds/{guild_id}/bans/{user_id}', guild_id=guild_id, user_id=user_id)
        return await self.request(route)