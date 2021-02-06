import aiohttp
import asyncio
import functools

from datetime import datetime

from .utils import (
    JsonStructure,
    JsonField,
    undefined
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

                    self.remaining -= 1
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
    __json_fields__ = {
        'global_ratelimit': JsonField('global'),
        'retry_after': JsonField('retry_after', float),
        'message': JsonField('message'),
    }

    global_ratelimit: bool
    retry_after: float
    message: str


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
            ratelimiter._reset = \
                datetime.now().timestamp() + (r.retry_after / 1000)

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

        req = functools.partial(
            self.client_session.request,
            meth,
            url,
            headers=headers,
            **kwargs
        )
        actual_req = functools.partial(self._request, ratelimiter, req)

        return ratelimiter.request(actual_req)

    def get_guild_audit_log(
        self,
        guild_id,
        *,
        user_id=undefined,
        action_type=undefined,
        before=undefined,
        limit=undefined
    ):
        params = {}

        if user_id is not undefined:
            params['user_id'] = user_id

        if action_type is not undefined:
            params['action_type'] = action_type

        if before is not undefined:
            params['before'] = before

        if limit is not undefined:
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
        *,
        name=undefined,
        channel_type=undefined,
        position=undefined,
        topic=undefined,
        nsfw=undefined,
        slowmode=undefined,
        bitrate=undefined,
        user_limit=undefined,
        permission_overwrites=undefined,
        parent_id=undefined
    ):
        payload = {
            'name': name,
            'type': channel_type,
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

    def get_channel_messages(
        self,
        channel_id,
        *,
        around=undefined,
        before=undefined,
        after=undefined,
        limit=undefined
    ):
        params = {}

        if around is not undefined:
            params['around'] = around

        if before is not undefined:
            params['before'] = before

        if after is not undefined:
            params['after'] = after

        if limit is not undefined:
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

    def send_message(
        self,
        channel_id,
        *,
        content=undefined,
        nonce=undefined,
        tts=False,
        embed=undefined
    ):
        payload = {}

        if content is not undefined:
            payload['content'] = content

        if nonce is not undefined:
            payload['nonce'] = nonce

        payload['tts'] = tts

        if embed is not undefined:
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
            'channels/{channel_id}/messages/{message_id}'
            '/reactions/{emoji}/@me',
            dict(channel_id=channel_id, message_id=message_id, emoji=emoji)
        )
        return fut

    def delete_reaction(
        self,
        channel_id,
        message_id,
        emoji,
        user_id=undefined
    ):
        if user_id is None:
            user_id = '@me'

        fut = self.request(
            'DELETE',
            'channels/{channel_id}/messages/{message_id}'
            '/reactions/{emoji}/{user_id}',
            dict(
                channel_id=channel_id,
                message_id=message_id,
                emoji=emoji,
                user_id=user_id
            )
        )
        return fut

    def get_reactions(self, channel_id, message_id):
        fut = self.request(
            'GET',
            'channels/{channel_id}/messages/{message_id}/reactions',
            dict(channel_id=channel_id, message_id=message_id)
        )
        return fut

    def delete_reactions(self, channel_id, message_id, emoji=undefined):
        path = 'channels/{channel_id}/messages/{message_id}/reactions'

        if emoji is not undefined:
            path += '/{emoji}'

        fut = self.request(
            'DELETE',
            path,
            dict(channel_id=channel_id, message_id=message_id, emoji=emoji)
        )
        return fut

    def edit_message(
        self,
        channel_id,
        message_id,
        *,
        content=undefined,
        embed=undefined,
        flags=undefined,
        allowed_mentions=undefined
    ):
        payload = {}

        if content is not undefined:
            payload['content'] = content

        if embed is not undefined:
            payload['embed'] = embed

        if flags is not undefined:
            payload['flags'] = flags

        if allowed_mentions is not undefined:
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
            'channels/{channel_id}/messages/{message_id}',
            dict(channel_id=channel_id, message_id=message_id)
        )
        return fut

    def bulk_delete_messages(self, channel_id, message_ids):
        payload = {
            'messages': message_ids
        }

        fut = self.request(
            'POST',
            'channels/{channel_id}/messages/bulk-delete',
            dict(channel_id=channel_id),
            json=payload
        )
        return fut

    def edit_channel_permissions(
        self,
        channel_id,
        overwrite_id,
        allow,
        deny,
        overwrite_type
    ):
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
        max_age=undefined,
        max_uses=undefined,
        temporary=undefined,
        unique=undefined,
        target_user_id=undefined,
        target_user_type=undefined
    ):
        payload = {}

        if max_age is not undefined:
            payload['max_age'] = max_age

        if max_uses is not undefined:
            payload['max_uses'] = max_uses

        if temporary is not undefined:
            payload['temporary'] = temporary

        if unique is not undefined:
            payload['unique'] = unique

        if target_user_id is not undefined:
            payload['target_user'] = target_user_id

        if target_user_type is not undefined:
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

    def create_guild_emoji(self, guild_id, name, image, roles=undefined):
        payload = {
            'name': name,
            'image': image,
        }

        if roles is not undefined:
            payload['roles'] = roles

        fut = self.request(
            'POST',
            'guilds/{guild_id}/eomjis',
            dict(guild_id=guild_id),
            json=payload
        )
        return fut

    def modify_guild_emoji(
        self,
        guild_id,
        emoji_id,
        name=undefined,
        roles=undefined
    ):
        payload = {}

        if name is not undefined:
            payload['name'] = name

        if roles is not undefined:
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

    def get_guild_preview(self, guild_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}/preview',
            dict(guild_id=guild_id),
        )
        return fut

    def modify_guild(
        self,
        guild_id,
        *,
        name=undefined,
        region=undefined,
        verification_level=undefined,
        default_message_notifications=undefined,
        explicit_content_filter=undefined,
        afk_channel_id=undefined,
        afk_timeout=undefined,
        icon=undefined,
        owner_id=undefined,
        splash=undefined,
        banner=undefined,
        system_channel_id=undefined,
        rules_channel_id=undefined,
        public_updates_channel_id=undefined,
        preferred_locale=undefined
    ):
        payload = {}

        if name is not undefined:
            payload['name'] = name

        if region is not undefined:
            payload['region'] = region

        if verification_level is not undefined:
            payload['verification_level'] = verification_level

        if default_message_notifications is not undefined:
            payload['default_message_notifications'] = \
                default_message_notifications

        if explicit_content_filter is not undefined:
            payload['explicit_content_filter'] = explicit_content_filter

        if afk_channel_id is not undefined:
            payload['adk_channel_id'] = afk_channel_id

        if afk_timeout is not undefined:
            payload['afk_timeout'] = afk_timeout

        if icon is not undefined:
            payload['icon'] = icon

        if owner_id is not undefined:
            payload['owner_id'] = owner_id

        if splash is not undefined:
            payload['splash'] = splash

        if banner is not undefined:
            payload['banner'] = banner

        if system_channel_id is not undefined:
            payload['system_channel_id'] = system_channel_id

        if rules_channel_id is not undefined:
            payload['rules_channel_id'] = rules_channel_id

        if public_updates_channel_id is not undefined:
            payload['public_updates_channel_id'] = public_updates_channel_id

        if preferred_locale is not undefined:
            payload['preferred_locale'] = preferred_locale

        fut = self.request(
            'PATCH',
            'guilds/{guild_id}',
            dict(guild_id=guild_id),
            json=payload
        )
        return fut

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

    def create_guild_channel(
        self,
        guild_id,
        *,
        name=undefined,
        channel_type=undefined,
        topic=undefined,
        bitrate=undefined,
        user_limit=undefined,
        slowmode=undefined,
        position=undefined,
        permission_overwrites=undefined,
        parent_id=undefined,
        nsfw=undefined
    ):
        payload = {}

        if name is not undefined:
            payload['name'] = name

        if channel_type is not undefined:
            payload['type'] = channel_type

        if topic is not undefined:
            payload['topic'] = topic

        if bitrate is not undefined:
            payload['bitrate'] = bitrate

        if user_limit is not undefined:
            payload['user_limit'] = user_limit

        if slowmode is not undefined:
            payload['rate_limt_per_user'] = slowmode

        if position is not undefined:
            payload['position'] = position

        if permission_overwrites is not undefined:
            payload['permission_overwrites'] = permission_overwrites

        if parent_id is not undefined:
            payload['parent_id'] = parent_id

        if nsfw is not undefined:
            payload['nsfw'] = nsfw

        fut = self.request(
            'POST',
            'guilds/{guild_id}/channels',
            dict(guild_id=guild_id),
            json=payload
        )
        return fut

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

    def get_guild_members(self, guild_id, limit=1000, after=undefined):
        params = {
            'limit': limit
        }

        if after is not undefined:
            params['after'] = after

        fut = self.request(
            'GET',
            'guilds/{guild_id}/members',
            dict(guild_id=guild_id),
            params=params
        )
        return fut

    def add_guild_member(
        self,
        guild_id,
        user_id,
        access_token,
        *,
        nick=undefined,
        roles=undefined,
        mute=undefined,
        deaf=undefined
    ):
        payload = {}

        if nick is not undefined:
            payload['nick'] = nick

        if roles is not undefined:
            payload['roles'] = roles

        if mute is not undefined:
            payload['mute'] = mute

        if deaf is not undefined:
            payload['deaf'] = deaf

        fut = self.request(
            'PUT',
            'guilds/{guild_id}/members/{user_id}',
            dict(guild_id=guild_id, user_id=user_id),
            json=payload
        )
        return fut

    def modify_guild_member(
        self,
        guild_id,
        user_id,
        *,
        nick=undefined,
        roles=undefined,
        mute=undefined,
        deaf=undefined,
        channel_id=undefined
    ):
        payload = {}

        if nick is not undefined:
            payload['nick'] = nick

        if roles is not undefined:
            payload['roles'] = roles

        if mute is not undefined:
            payload['mite'] = mute

        if deaf is not undefined:
            payload['deaf'] = deaf

        if channel_id is not undefined:
            payload['channel_id'] = channel_id

        fut = self.request(
            'PATCH',
            'guilds/{guild_id}/members/{user_id}',
            dict(guild_id=guild_id, user_id=user_id),
            json=payload
        )
        return fut

    def modify_client_nick(self, guild_id, nick):
        payload = {
            'nick': nick
        }

        fut = self.request(
            'PATCH',
            'guilds/{guild_id}/members/@me/nick',
            dict(guild_id=guild_id),
            json=payload
        )
        return fut

    def add_guild_member_role(self, guild_id, user_id, role_id):
        fut = self.request(
            'PUT',
            'guilds/{guild_id}/members/{user_id}/roles{role_id}',
            dict(guild_id=guild_id, user_id=user_id, role_id=role_id)
        )
        return fut

    def remove_guild_member_role(self, guild_id, user_id, role_id):
        fut = self.request(
            'DELETE',
            'guilds/{guild_id}/members/{user_id}/roles{role_id}',
            dict(guild_id=guild_id, user_id=user_id, role_id=role_id)
        )
        return fut

    def kick_guild_member(self, guild_id, user_id):
        fut = self.request(
            'DELETE',
            'guilds/{guild_id}/members/{user_id}',
            dict(guild_id=guild_id, user_id=user_id)
        )
        return fut

    def get_guild_bans(self, guild_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}/bans',
            dict(guild_id=guild_id)
        )
        return fut

    def get_guild_ban(self, guild_id, user_id):
        fut = self.request(
            'GET',
            'guild/{guild_id}/bans/{user_id}',
            dict(guild_id=guild_id, user_id=user_id)
        )
        return fut

    def create_guild_ban(
        self,
        guild_id,
        user_id,
        delete_message_days=undefined,
        reason=undefined
    ):
        payload = {}

        if delete_message_days is not undefined:
            payload['delete_message_days'] = delete_message_days

        if reason is not undefined:
            payload['reason'] = reason

        fut = self.request(
            'PUT',
            'guilds/{guild_id}/bans/{user_id}',
            dict(guild_id=guild_id, user_id=user_id),
            json=payload
        )
        return fut

    def remove_guild_ban(self, guild_id, user_id):
        fut = self.request(
            'DELETE',
            'guilds/{guild_id}/bans/{user_id}',
            dict(guild_id=guild_id, user_id=user_id)
        )
        return fut

    def get_guild_roles(self, guild_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}/roles',
            dict(guild_id=guild_id)
        )
        return fut

    def create_guild_role(
        self,
        guild_id,
        *,
        name=undefined,
        permissions=undefined,
        color=undefined,
        hoist=undefined,
        mentionable=undefined
    ):
        payload = {}

        if name is not undefined:
            payload['name'] = name

        if permissions is not undefined:
            payload['permissions'] = permissions

        if color is not undefined:
            payload['color'] = color

        if hoist is not undefined:
            payload['hoist'] = hoist

        if mentionable is not undefined:
            payload['mentionable'] = mentionable

        fut = self.request(
            'POST',
            'guilds/{guild_id}/roles',
            dict(guild_id=guild_id),
            json=payload
        )
        return fut

    def modify_guild_role_positions(self, guild_id, positions):
        fut = self.request(
            'PATCH',
            'guilds/{guild_id}/roles',
            dict(guild_id=guild_id),
            json=positions
        )
        return fut

    def modify_guild_role(
        self,
        guild_id,
        role_id,
        *,
        name=undefined,
        permissions=undefined,
        color=undefined,
        hoist=undefined,
        mentionable=undefined
    ):
        payload = {}

        if name is not undefined:
            payload['name'] = name

        if permissions is not undefined:
            payload['permissions'] = permissions

        if color is not undefined:
            payload['color'] = color

        if hoist is not undefined:
            payload['hoist'] = hoist

        if mentionable is not undefined:
            payload['mentionable'] = mentionable

        fut = self.request(
            'PATCH',
            'guilds/{guild_id}/roles/{role_id}',
            dict(guild_id=guild_id, role_id=role_id),
            json=payload
        )
        return fut

    def delete_guild_role(self, guild_id, role_id):
        fut = self.request(
            'DELETE',
            'guild/{guild_id}/roles/{role_id}',
            dict(guild_id=guild_id, role_id=role_id)
        )
        return fut

    def get_guild_prune_count(
        self,
        guild_id,
        *,
        days=undefined,
        include_roles=undefined
    ):
        params = {}

        if days is not undefined:
            params['days'] = days

        if include_roles is not undefined:
            params['include_roles'] = include_roles

        fut = self.request(
            'GET',
            'guilds/{guild_id}/prune',
            dict(guild_id=guild_id),
            params=params
        )
        return fut

    def begin_guild_prune(
        self,
        guild_id,
        *,
        days=undefined,
        include_roles=undefined,
        compute_prune_count=undefined
    ):
        payload = {}

        if days is not undefined:
            payload['days'] = days

        if include_roles is not undefined:
            payload['include_roles'] = include_roles

        if compute_prune_count is not undefined:
            payload['compute_prune_count'] = compute_prune_count

        fut = self.request(
            'GET',
            'guilds/{guild_id}/prune',
            dict(guild_id=guild_id),
            json=payload
        )
        return fut

    def get_guild_voice_region(self, guild_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}/regions',
            dict(guild_id=guild_id)
        )
        return fut

    def get_guild_invites(self, guild_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}/invites',
            dict(guild_id=guild_id)
        )
        return fut

    def get_guild_integrations(self, guild_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}/integrations',
            dict(guild_id=guild_id)
        )
        return fut

    def create_guild_integration(
        self,
        guild_id,
        integration_type,
        integration_id
    ):
        payload = {
            'type': integration_type,
            'id': integration_id
        }

        fut = self.request(
            'GET',
            'guild/{guild_id}/integrations/',
            dict(guild_id=guild_id),
            json=payload
        )
        return fut

    def modify_guild_integration(
        self,
        guild_id,
        integration_id,
        *,
        expire_behavior=undefined,
        expire_grace_period=undefined,
        enable_emoticons=undefined
    ):
        payload = {}

        if expire_behavior is not undefined:
            payload['expire_behavior'] = expire_behavior

        if expire_grace_period is not undefined:
            payload['expire_grace_period'] = expire_grace_period

        if enable_emoticons is not undefined:
            payload['enable_emoticons'] = enable_emoticons

        fut = self.request(
            'PATCH',
            'guilds/{guild_id}/integrations/{integration_id}',
            dict(guild_id=guild_id, integration_id=integration_id),
            json=payload
        )
        return fut

    def delete_guild_integration(self, guild_id, integration_id):
        fut = self.request(
            'DELETE',
            'guilds/{guild_id}/integrations/{integration_id}',
            dict(guild_id=guild_id, integration_id=integration_id)
        )
        return fut

    def sync_guild_integration(self, guild_id, integration_id):
        fut = self.request(
            'POST',
            'guilds/{guild_id}/integrations/{integration_id}/sync',
            dict(guild_id=guild_id, integration_id=integration_id)
        )
        return fut

    def get_guild_widget_settings(self, guild_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}/widget',
            dict(guild_id=guild_id)
        )
        return fut

    def modify_guild_widget(
        self,
        guild_id,
        *,
        enabled=undefined,
        channel_id=undefined
    ):
        payload = {}

        if enabled is not undefined:
            payload['enabled'] = enabled

        if channel_id is not undefined:
            payload['channel_id'] = channel_id

        fut = self.request(
            'PATCH',
            'guilds/{guild_id}/widget',
            dict(guild_id=guild_id),
            json=payload
        )
        return fut

    def get_guild_widget(self, guild_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}/widget.json',
            dict(guild_id=guild_id)
        )
        return fut

    def get_guild_vanity_url(self, guild_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}/vanity-url',
            dict(guild_id=guild_id)
        )
        return fut

    def get_guild_widget_image(self, guild_id, style=undefined):
        params = {}

        if style is not undefined:
            params['style'] = style

        fut = self.request(
            'GET',
            'guilds/{guild_id}/widget.png',
            dict(guild_id=guild_id),
            params=params
        )
        return fut

    def get_invite(self, invite_code, with_counts=undefined):
        params = {}

        if with_counts is not undefined:
            params['with_counts'] = with_counts

        fut = self.request(
            'GET',
            'invites/{invite_code}',
            dict(invite_code=invite_code),
            params=params
        )
        return fut

    def delete_invite(self, invite_code):
        fut = self.request(
            'GET',
            'invites/{invite_code}',
            dict(invite_code=invite_code)
        )
        return fut

    def get_template(self, template_code):
        fut = self.request(
            'GET',
            'guilds/templates/{template_code}',
            dict(template_code=template_code)
        )
        return fut

    def create_guild_from_template(
        self,
        template_code,
        *,
        name=undefined,
        icon=undefined
    ):
        payload = {}

        if name is not undefined:
            payload['name'] = name

        if icon is not undefined:
            payload['icon'] = icon

        fut = self.request(
            'POST',
            'guilds/templates/{template_code}',
            dict(template_code=template_code),
            json=payload
        )
        return fut

    def get_guild_templates(self, guild_id):
        fut = self.request(
            'GET',
            'guilds/{guild_id}/templates',
            dict(guild_id=guild_id)
        )
        return fut

    def create_guild_template(
        self,
        guild_id,
        *,
        name=undefined,
        description=undefined
    ):
        payload = {}

        if name is not undefined:
            payload['name'] = name

        if description is not undefined:
            payload['description'] = description

        fut = self.request(
            'POST',
            'guilds/{guild_id}/templates',
            dict(guild_id=guild_id),
            json=payload
        )
        return fut

    def sync_guild_template(self, guild_id, template_code):
        fut = self.request(
            'PUT',
            'guilds/{guild_id}/templates/{template_code}',
            dict(guild_id=guild_id, template_code=template_code)
        )
        return fut

    def modify_guild_template(
        self,
        guild_id,
        template_code,
        name=undefined,
        description=undefined
    ):
        payload = {}

        if name is not undefined:
            payload['name'] = name

        if description is not undefined:
            payload['description'] = description

        fut = self.request(
            'POST',
            'guilds/{guild_id}/templates/{template_code}',
            dict(guild_id=guild_id, template_code=template_code),
            json=payload
        )
        return fut

    def delete_guild_template(self, guild_id, template_code):
        fut = self.request(
            'DELETE',
            'guilds/{guild_id}/templates/{template_code}',
            dict(guild_id=guild_id, template_code=template_code)
        )
        return fut

    def get_user(self, user_id='@me'):
        fut = self.request(
            'GET',
            'users/{user_id}',
            dict(user_id=user_id)
        )
        return fut

    def modify_client_user(self, username=undefined, avatar=undefined):
        payload = {}

        if username is not undefined:
            payload['username'] = username

        if avatar is not undefined:
            payload['avatar'] = avatar

        fut = self.request(
            'PATCH',
            'users/@me',
            dict(),
            json=payload
        )
        return fut

    def get_client_guilds(
        self,
        before=undefined,
        after=undefined,
        limit=undefined
    ):
        params = {}

        if before is not undefined:
            params['before'] = before

        if after is not undefined:
            params['after'] = after

        if limit is not undefined:
            params['limit'] = limit

        fut = self.request(
            'PATCH',
            'users/@me/guilds',
            dict(),
            params=params
        )
        return fut

    def leave_guild(self, guild_id):
        fut = self.request(
            'DELETE',
            'users/@me/guilds/{guild_id}',
            dict(),
        )
        return fut

    def get_client_dms(self):
        fut = self.request(
            'GET',
            'users/@me/channels',
            dict(),
        )
        return fut

    def create_dm_channel(self, recipient_id):
        payload = {
            'recipient_id': recipient_id
        }

        fut = self.request(
            'POST',
            'users/@me/channels',
            dict(),
            json=payload
        )
        return fut

    def create_group_dm_channel(self, access_tokens, nicks=undefined):
        payload = {
            'access_tokens': access_tokens
        }

        if nicks is not undefined:
            payload['nicks'] = nicks

        fut = self.request(
            'POST',
            'users/@me/channels',
            dict(),
            json=payload
        )
        return fut

    def get_client_connections(self):
        fut = self.request(
            'GET',
            'users/@me/connections',
            dict()
        )
        return fut

    def get_gateway_bot(self):
        url = self.URL + 'gateway/bot'
        ratelimiter = Ratelimiter(self)

        base_headers = {
            'Authorization': f'Bot {self._client.token}'
        }

        req = functools.partial(
            self.client_session.request,
            'GET',
            url,
            headers=base_headers
        )
        actual_req = functools.partial(self._request, ratelimiter, req)
        return ratelimiter.request(actual_req)
