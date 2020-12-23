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

    def get_guild_audit_log(self, guild_id, *, user_id=None, action_type=None, before=None, limit=None):
        params = {}

        if user_id is not None:
            params['user_id'] = user_id

        if action_type is not None:
            params['action_type'] = action_type

        if before is not None:
            params['before'] = before

        if limit is not None:
            params['before'] = before

        fut = self.request(
            'GET',
            'guilds/{guild_id}/audit-logs',
            dict(guild_id=guild_id),
            params=params
        )
        return fut

    def get_channel(self, channel_id):
        fut = self.request(
            'GET', 
            'channels/{channel_id}',
            dict(channel_id=channel_id)
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
            'channels/{channel_id}',
            dict(channel_id=channel_id)
        )
        return fut

    def get_channel_messages(self, channel_id, *, around=None, before=None, after=None, limit=None):
        params = {}

        if around is not None:
            params['around'] = around

        if before is not None:
            params['before'] = before

        if after is not None:
            params['after'] = after

        if limit is not None:
            params['limit'] = limit

        fut = self.request(
            'GET',
            'channels/{channel_id}/messages',
            dict(channel_id=channel_id),
            params=params
        )
        return fut

    def get_channel_message(self, channel_id, message_id):
        fut = self.request(
            'GET',
            'channels/{channel_id}/messages/{message_id}',
            dict(channel_id=channel_id, message_id=message_id)
        )
        return fut

    def send_message(self, channel_id, *, content=None, nonce=None, tts=False, embed=None):
        payload = {}

        if content is not None:
            payload['content'] = content

        if nonce is not None:
            payload['nonce'] = nonce

        payload['tts'] = tts

        if embed is not None:
            payload['embed'] = embed

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

    def create_reaction(self, channel_id, message_id, emoji):
        fut = self.request(
            'PUT',
            'channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me',
            dict(channel_id=channel_id, message_id=message_id, emoji=emoji)
        )
        return fut

    def delete_reaction(self, channel_id, message_id, emoji, user_id='@me'):
        fut = self.request(
            'DELETE',
            'channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}',
            dict(channel_id=channel_id, message_id=message_id, emoji=emoji, user_id=user_id)
        )
        return fut

    def get_reactions(self, channel_id, message_id):
        fut = self.request(
            'GET',
            'channels/{channel_id}/messages/{message_id}/reactions',
            dict(channel_id=channel_id, message_id=message_id)
        )
        return fut

    def delete_reactions(self, channel_id, message_id, emoji=None):
        path = 'channels/{channel_id}/messages/{message_id}/reactions'

        if emoji is not None:
            path += '/{emoji}'

        fut = self.request(
            'DELETE',
            path,
            dict(channel_id=channel_id, message_id=message_id, emoji=emoji)
        )
        return fut

    def edit_message(self, channel_id, message_id, *, content=None, embed=None, flags=None, allowed_mentions=None):
        payload = {}

        if content is not None:
            payload['content'] = content

        if embed is not None:
            payload['embed'] = embed

        if flags is not None:
            payload['flags'] = flags

        if allowed_mentions is not None:
            payload['allowed_mentions'] = allowed_mentions

        fut = self.request(
            'PATCH',
            'channels/{channel_id}/messages/{message_id}',
            dict(channel_id=channel_id, message_id=message_id),
            json=payload
        )
        return fut

    def delete_message(self, channel_id, message_id):
        fut = self.request(
            'DELETE',
            'channels/{channel_id}/messages/{message_id}'
        )
        return fut

    def bulk_delete_messages(self, channel_id, message_ids):
        payload = {
            'messages': message_ids
        }

        fut = self.request(
            'POST',
            'channels/{channel_id}/messages/bulk-delete',
            json=payload
        )
        return fut

    def edit_channel_permissions(self, channel_id, overwrite_id, allow, deny, overwrite_type):
        payload = {
            'allow': allow,
            'deny': deny,
            'type': overwrite_type
        }

        fut = self.request(
            'PATCH',
            'channels/{channel_id}/permissions/{overwrite_id}',
            dict(channel_id=channel_id, overwrite_id=overwrite_id),
            json=payload
        )
        return fut

    def get_channel_invites(self, channel_id):
        fut = self.request(
            'GET',
            'channels/{channel_id}/invites',
            dict(channel_id=channel_id)
        )
        return fut

    def create_channel_invite(
        self,
        channel_id,
        *,
        max_age=None,
        max_uses=None,
        temporary=False,
        unique=False,
        target_user_id=None,
        target_user_type=None
    ):
        payload = {}

        if max_age is not None:
            payload['max_age'] = max_age

        if max_uses is not None:
            payload['max_uses'] = max_uses

        payload['temporary'] = temporary

        payload['unique'] = unique

        if target_user_id is not None:
            payload['target_user'] = target_user_id

        if target_user_type is not None:
            payload['target_user_type'] = target_user_type

        fut = self.request(
            'POST',
            'channels/{channel_id}/invites',
            dict(channel_id=channel_id),
            json=payload
        )
        return fut

    def delete_channel_permission(self, channel_id, overwrite_id):
        fut = self.request(
            'DELETE',
            'channels/{channel_id}/permissions/{overwrite_id}',
            dict(channel_id=channel_id, overwrite_id=overwrite_id)
        )
        return fut

    def follow_news_channel(self, channel_id, webhook_channel_id):
        payload = {
            'webgook_channel_id': webhook_channel_id
        }

        fut = self.request(
            'POST',
            'channels/{channel_id}/followers',
            dict(channel_id=channel_id),
            json=payload
        )
        return fut

    def trigger_typing(self, channel_id):
        fut = self.request(
            'POST',
            'channels/{channel_id}/typing',
            dict(channel_id=channel_id)
        )
        return fut

    def get_pinned_messages(self, channel_id):
        fut = self.request(
            'GET',
            'channels/{channel_id}/pins',
            dict(channel_id=channel_id)
        )
        return fut

    def pin_message(self, channel_id, message_id):
        fut = self.request(
            'PUT',
            'channels/{channel_id}/pins/{message_id}',
            dict(channel_id=channel_id, message_id=message_id)
        )
        return fut

    def unpin_message(self, channel_id, message_id):
        fut = self.request(
            'DELETE',
            'channels/{channel_id}/pins/{message_id}',
            dict(channel_id=channel_id, message_id=message_id)
        )
        return fut

    def add_dm_recipient(self, channel_id, user_id, access_token, nick):
        payload = {
            'access_token': access_token,
            'nick': nick
        }

        fut = self.request(
            'POST',
            '/channels/{channel_id}/recipients/{user_id}',
            dict(channel_id=channel_id, user_id=user_id),
            json=payload
        )
        return fut

    def remove_dm_recipient(self, channel_id, user_id):
        fut = self.request(
            'DELETE',
            '/channels/{channel_id}/recipients/{user_id}',
            dict(channel_id=channel_id, user_id=user_id),
        )
        return fut

    def get_guild_emojis(self, guild_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}/emojis',
            dict(guild_id=guild_id)
        )
        return fut

    def get_guild_emoji(self, guild_id, emoji_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}/emojis/{emoji_id}',
            dict(guild_id=guild_id, emoji_id=emoji_id)
        )
        return fut

    def create_guild_emoji(self, guild_id, name, image, roles=None):
        payload = {
            'name': name,
            'image': image,
        }

        if roles is not None:
            payload['roles'] = roles

        fut = self.request(
            'POST',
            'guilds/{guild_id}/eomjis',
            dict(guild_id=guild_id),
            json=payload
        )
        return fut

    def modify_guild_emoji(self, guild_id, emoji_id, name=None, roles=None):
        payload = {}

        if name is not None:
            payload['name'] = name

        if roles is not None:
            payload['roles'] = roles

        fut = self.request(
            'PATCH',
            'guild/{guild_id}/emojis/{emoji_id}',
            dict(guild_id=guild_id, emoji_id=emoji_id),
            json=payload
        )
        return fut

    def delete_guild_emoji(self, guild_id, emoji_id):
        fut = self.request(
            'DELETE',
            'guilds/{guild_id}/emojis/{emoji_id}',
            dict(guild_id=guild_id, emoji_id=emoji_id)
        )
        return fut

    def get_guild(self, guild_id, with_counts=True):
        params = {
            'with_counts': with_counts
        }

        fut = self.request(
            'GET',
            'guilds/{guild_id}',
            dict(guild_id=guild_id),
            params=params
        )
        return fut

    def get_preview_guild(self, guild_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}/preview',
            dict(guild_id=guild_id),
        )
        return fut

    # modify_guild :(

    def delete_guild(self, guild_id):
        fut = self.request(
            'DELETE',
            'guilds/{guild_id}',
            dict(guild_id=guild_id),
        )
        return fut

    def get_guild_channels(self, guild_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}/channels',
            dict(guild_id=guild_id),
        )
        return fut

    # create_guild_channel :(

    def modify_guild_channel_positions(self, guild_id, positions):
        fut = self.request(
            'PATCH',
            'guilds/{guild_id}/channels',
            dict(guild_id=guild_id),
            json=positions
        )
        return fut

    def get_guild_member(self, guild_id, user_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}/members/{user_id}',
            dict(guild_id=guild_id, user_id=user_id)
        )
        return fut

    def get_guild_members(self, guild_id, limit=1000, after=None):
        params = {
            'limit': limit
        }

        if after is not None:
            params['after'] = after

        fut = self.request(
            'GET',
            'guilds/{guild_id}/members',
            dict(guild_id=guild_id),
            params=params
        )
        return fut

    # add_guild_member :(

    def get_user(self, user_id):
        fut = self.request(
            'GET',
            'users/{user_id}',
            dict(user_id=user_id)
        )
        return fut

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
            '/channels/{channel_id}'
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