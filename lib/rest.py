import aiohttp
import asyncio
import functools

from datetime import datetime

from .utils import (
    JsonStructure,
    JsonField
)
from .embed import Embed

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
        def set_result(resp):
            self._tasks.remove(task)
            fut.set_result(resp)

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
        print(self.current_burst_task,self.ready)
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

class MessageCreateRequest(JsonStructure):
<<<<<<< HEAD
    content = JsonField(str, 'content')
    nonce = JsonField(None, 'nonce')
    tts = JsonField(bool, 'tts')
    embed = JsonField(Embed, 'embed')
=======
    content = JsonField('content')
    nonce = JsonField('nonce')
    tts = JsonField('tts')
>>>>>>> e810744b1df8f73a495827a81b82bb0d3316a894
    #file
    #payload_json
    #allowed_mentions
    #message_reference

    def __init__(self, content=None, nonce=None, tts=None, embed=None):
        self.content = content
        self.nonce = nonce
        self.tts = tts
        self.embed = embed
                
class RestSession:
    URL = 'https://discord.com/api/v7/'
    def __init__(self, manager):
        self.manager = manager
        self.loop = manager.loop

        self.ratelimiters = {}
        self.client_session = aiohttp.ClientSession()
        
        self.base_headers = {
            'Authorization': f'Bot {self.manager.token}'
        }

    async def _request(self, ratelimiter, req):
        resp = await req()
        print(await resp.text())

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
                    path_params.get("guild_id"), path_params.get("channel_id"), path_params.get("webhook_id")
                )
        headers = kwargs.pop('headers', {})

        headers.update(self.base_headers)
        ratelimiter = self.ratelimiters.get(bucket)

        if ratelimiter is None:
            ratelimiter = Ratelimiter(self)
            self.ratelimiters[bucket] = ratelimiter

        req = functools.partial(self.client_session.request, meth, url, headers=headers, **kwargs)
        actual_req = functools.partial(self._request, ratelimiter, req)

        return ratelimiter.request(actual_req)

    # Getting stuff

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

    def get_member(self, user_id, guild_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}/members/{user_id}',
            dict(user_id=user_id, guild_id=guild_id)
        )
        return fut

    #Modify Channel

    def delete_channel(self, channel_id):
        fut = self.request(
            'DELETE',
            'channels/{channel_id}',
            dict(channel_id=channel_id)
        )
        return fut

    #get message

    def get_channel_message(self, channel_id, message_id):
        fut = self.request(
            'GET',
            'channels/{channel_id}/messages/{message_id}',
            dict(channel_id=channel_id, message_id=message_id)
        )
        return fut

    def send_message(self, channel_id, content=None, nonce=None, tts=False):
        req = MessageCreateRequest(content, nonce, tts)
        fut = self.request(
            'POST',
            'channels/{channel_id}/messages',
            dict(channel_id=channel_id),
            json=req.to_dict()
        )
        return fut