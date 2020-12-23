import aiohttp
import asyncio
import functools

from datetime import datetime

from .utils import (
    JsonStructure,
    JsonField
)


class Ratelimiter:
    def __init__(self, rest_session):
        self.rest_session = rest_session
        self.loop = rest_session.loop

        self.limit = float('inf')
        self._remaining = float('inf')
        self._reset = float('inf')

        self.lock = asyncio.Lock()

        self.queue = []
        self._tasks = []

        self.current_burst_task: asyncio.Task = None

    @property
    def reset_after(self):
        now = datetime.now().timestamp()
        if now > self._reset:
            self._reset = 0
        return max((0, self._reset - now))

    @property
    def remaining(self):
        if self.reset_after == 0:
            self._remaining = self.limit
        return self._remaining

    @remaining.setter
    def remaining(self, value):
        self._remaining = value

    @property
    def ready(self):
        return all(
            attr != float('inf') 
            for attr in (
                self.limit, 
                self._reset, 
                self._remaining
            )
        )
    
    def _task_done_callback(self, task, fut):
        def set_result(task):
            self._tasks.remove(task)
            fut.set_result(task.result())

        task.add_done_callback(set_result)

    def _burst_run_once(self):
        req, fut = self.queue.pop(0)
        task = self.loop.create_task(req())

        self._tasks.append(task)
        self._task_done_callback(task, fut)

    async def do_burst(self):
        async with self.lock:
            if not self.ready:
                self._burst_run_once()
            else:
                while self.queue:
                    await asyncio.sleep(0)
                    if self.remaining == 0:
                        await asyncio.sleep(self.reset_after)

                    self.remaining -= 1 #good safety mesaure
                    self._burst_run_once()

            self.current_burst_task = None

    def request(self, req):
        fut = self.loop.create_future()

        self.queue.append((req, fut))
        if not self.ready:
            self.loop.create_task(self.do_burst())

        elif self.current_burst_task is None:
            self.current_burst_task = self.loop.create_task(self.do_burst())

        return fut


class RatelimitedResponse(JsonStructure):
    global_ratelimit = JsonField('global')
    retry_after = JsonField('retry_after', float)
    message = JsonField('message')

    def __init__(self, content=None, nonce=None, tts=None, embed=None):
        self.content = content
        self.nonce = nonce
        self.tts = tts
        self.embed = embed


class RestSession:
    URL = 'https://discord.com/api/v7/'

    def __init__(self, client):
        self._client = client
        self.loop = self._client.loop

        self.ratelimiters = {}
        self.client_session = aiohttp.ClientSession()

    async def _request(self, ratelimiter, req):
        resp = await req()

        if resp.status == 429:
            print('429!!!!!!!!!!!!!')
            if ratelimiter.current_burst_task is not None:
                ratelimiter.current_burst_task.cancel()

            data = await resp.text()
            r = RatelimitedResponse.unmarshal(data)

            ratelimiter.remaining = 0
            ratelimiter._reset = datetime.now().timestamp() + (r.retry_after / 1000)

            return await ratelimiter.request(req)

        limit = resp.headers.get('X-Ratelimit-Limit')
        remaining = resp.headers.get('X-Ratelimit-Remaining')
        reset = resp.headers.get('X-Ratelimit-Reset')

        if limit is not None:
            ratelimiter.limit = int(limit)

        if remaining is not None:
            ratelimiter.remaining = int(remaining)

        if reset is not None:
            ratelimiter._reset = float(reset)

        return resp

    def request(self, meth, url, path_params, **kwargs):
        url = self.URL + url.format(**path_params)

        bucket = '{0}-{1}-{2}-{3}'.format(
                    meth, 
                    path_params.get("guild_id"), 
                    path_params.get("channel_id"), 
                    path_params.get("webhook_id")
                )
        headers = kwargs.pop('headers', {})

        base_headers = {
            'Authorization': f'Bot {self._client.token}'
        }

        headers.update(base_headers)
        ratelimiter = self.ratelimiters.get(bucket)

        if ratelimiter is None:
            ratelimiter = Ratelimiter(self)
            self.ratelimiters[bucket] = ratelimiter

        req = functools.partial(self.client_session.request, meth, url, headers=headers, **kwargs)
        actual_req = functools.partial(self._request, ratelimiter, req)

        return ratelimiter.request(actual_req)


    def get_channel(self, channel_id):
        fut = self.request(
            'GET', 
            'channels/{channel_id}',
            dict(channel_id=channel_id)
        )
        return fut

    def get_guild(self, guild_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}',
            dict(guild_id=guild_id)
        )
        return fut

    def get_user(self, user_id):
        fut = self.request(
            'GET',
            'users/{user_id}',
            dict(user_id=user_id)
        )
        return fut

    def get_guild_member(self, user_id, guild_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}/members/{user_id}',
            dict(user_id=user_id, guild_id=guild_id)
        )
        return fut

    #get channel messages

    def get_channel_message(self, channel_id, message_id):
        fut = self.request(
            'GET',
            'channels/{channel_id}/messages/{message_id}',
            dict(channel_id=channel_id, message_id=message_id)
        )
        return fut

    def delete_channel(self, channel_id):
        fut = self.request(
            'DELETE',
            'channels/{channel_id}',
            dict(channel_id=channel_id)
        )
        return fut

    def get_channel_message(self, channel_id, message_id):
        fut = self.request(
            'GET',
            'channels/{channel_id}/messages/{message_id}',
            dict(channel_id=channel_id, message_id=message_id)
        )
        return fut

    def modify_channel(
        self, 
        channel_id, 
        name=None, 
        type=None, 
        position=None, 
        topic=None, 
        nsfw=None, 
        slowmode=None, 
        bitrate=None, 
        user_limit=None, 
        permission_overwrites=None, 
        parent_id=None
    ):
        payload = {
            'name': name,
            'type': type,
            'position': position,
            'topic': topic,
            'nsfw': nsfw,
            'ratelimit_per_user': slowmode,
            'bitrate': bitrate,
            'user_limit': user_limit,
            'permission_overwrites': permission_overwrites,
            'parent_id': parent_id
        }
        fut = self.request(
            'PATCH',
            'channels/{channel_id}',
            dict(channel_id=channel_id),
            json=payload
        )
        return fut

    def delete_channel(self, channel_id):
        fut = self.request(
            'DELETE',
            '/channels/{channel_id}'
        )
        return fut

    def send_message(self, channel_id, content=None, nonce=None, tts=False):
        payload = {
            'content': content,
            'nonce': nonce,
            'tts': tts
        }
        fut = self.request(
            'POST',
            'channels/{channel_id}/messages',
            dict(channel_id=channel_id),
            json=payload
        )
        return fut

    def crosspost_message(self, channel_id, message_id):
        fut = self.request(
            'POST',
            'channels/{channel_id}/messages/{message_id}/crosspost',
            dict(channel_id=channel_id, message_id=message_id)
        )
        return fut

    def get_gateway_bot(self):
        url = self.URL + 'gateway/bot'
        ratelimiter = Ratelimiter(self)

        base_headers = {
            'Authorization': f'Bot {self._client.token}'
        }

        req = functools.partial(self.client_session.request, 'GET', url, headers=base_headers)
        actual_req = functools.partial(self._request, ratelimiter, req)
        return ratelimiter.request(actual_req)