from .baseobject import BaseObject
from .. import rest
from ..clients.client import ClientClasses
from ..enums import ChannelType
from ..utils import JsonArray, JsonField, Snowflake, undefined


def _modify_helper(name, position, permission):
    json = {}

    if name is not None:
        if not isinstance(name, str):
            raise TypeError(f'name should be a str or None, got {name.__class__.__name__!r}')

        json['name'] = name

    if position is not undefined:
        if not isinstance(position, int):
            raise TypeError(f'position should be an int, got {position.__class__.__name__!r}')

        json['position'] = position

    return json


class GuildChannel(BaseObject):
    __slots__ = ('permissions',)

    name = JsonField('name')
    guild_id = JsonField('guild_id', Snowflake)
    position = JsonField('position')
    nsfw = JsonField('nsfw')
    parent_id = JsonField('parent_id', Snowflake)
    type = JsonField('type', ChannelType.get_enum)

    def __init__(self, *, state):
        super().__init__(state=state)

        self.permissions = ClientClasses.PermissionOverwriteState(
            client=self.state.client, channel=self
        )

    @property
    def mention(self):
        return f'<#{self.id}>'

    @property
    def guild(self):
        return self.state.client.guilds.get(self.guild_id)

    @property
    def parent(self):
        return self.state.client.channels.get(self.parent_id)

    async def delete(self):
        return self.state.delete(self.id)

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        guild = self.guild
        if guild is not None:
            guild.channels._keys.add(self.id)

        permission_overwrites = data.get('permission_overwrites')
        if permission_overwrites is not None:
            overwrites = set()

            for overwrite in permission_overwrites:
                overwrites.add(self.permissions.upsert(overwrite).id)

            for overwrite_id in set(self.permissions.keys()) - overwrites:
                del self.permissions.mapping[overwrite_id]


class TextChannel(GuildChannel):
    __slots__ = ('messages', 'last_pin_timestamp')

    topic = JsonField('topic')
    slowmode = JsonField('rate_limit_per_user')
    last_message_id = JsonField('last_message_id', Snowflake)

    def __init__(self, *, state):
        super().__init__(state=state)

        self.last_pin_timestamp = None
        self.messages = ClientClasses.MessageState(client=self.state.client, channel=self)

    def __str__(self):
        return f'#{self.name}'

    async def modify(
        self, *, name=None, type=None, position=undefined, topic=undefined, nsfw=undefined,
        slowmode=undefined, permissions=undefined, parent=undefined,
        thread_archive_duration=undefined
    ):
        json = _modify_helper(name, position, permissions)

        if type is not None:
            json['type'] = ChannelType.get_value(type)

        if topic is not undefined:
            if topic is not None and not isinstance(topic, undefined):
                raise TypeError(f'topic should be a str or None, got {topic.__class__.__name__!r}')

            json['topic'] = topic

        if nsfw is not undefined:
            if nsfw is not None and not isinstance(nsfw, bool):
                raise TypeError(f'nsfw should be a bool or None, got {nsfw.__class__.__name__!r}')

            json['nsfw'] = nsfw

        if slowmode is not undefined:
            if slowmode is not None and not isinstance(slowmode, int):
                raise TypeError(
                    f'slowmode should be an int or None, got {slowmode.__class__.__name__!r}'
                )

        if parent is not undefined:
            if parent is not None:
                json['parent_id'] = Snowflake.try_snowflake(parent)
            else:
                json['parent_id'] = None

        if thread_archive_duration is not undefined:
            if thread_archive_duration is not None and not isinstance(thread_archive_duration, int):
                raise TypeError(
                    f'thread_archive_duration should be an int or None, '
                    f'got {thread_archive_duration.__class__.__name__!r}'
                )

            json['thread_archive_duration'] = thread_archive_duration

        data = await rest.modify_channel.request(
            self.state.client.rest, dict(channel_id=self.id), json=json
        )

        return self.state.upsert(data)

    async def add_follower(self, channel):
        channel_id = Snowflake.try_snowflake(channel)

        data = await rest.follow_news_channel.request(
            session=self.state.client.rest, fmt=dict(channel_id=self.id),
            params=dict(webhook_channel_id=channel_id)
        )

        return Snowflake(data['webhook_id'])

    async def typing(self):
        await rest.trigger_typing_indicator.request(
            session=self.state.client.rest, fmt=dict(channel_id=self.id)
        )

    async def fetch_pins(self):
        data = await rest.get_pinned_messages.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.id))

        return [self.messages.upsert(message) for message in data]


class CategoryChannel(GuildChannel):
    def __str__(self):
        return f'#{self.name}'

    def iterchildren(self):
        for channel in self.guild.channels:
            if channel.parent_id == self.id:
                yield channel

    async def modify(self, *, name=None, position=undefined, permissions=undefined):
        json = _modify_helper(name, position, permissions)

        data = await rest.modify_channel.request(
            self.state.client.rest, dict(channel_id=self.id), json=json
        )

        return self.state.upsert(data)


class VoiceChannel(GuildChannel):
    bitrate = JsonField('bitrate')
    user_limit = JsonField('user_limit')

    def __str__(self):
        return f'#!{self.name}'

    async def modify(
        self, *, name=None, position=undefined, bitrate=undefined, user_limit=undefined,
        permissions=undefined, parent=undefined, rtc_origin=undefined, video_quality_mode=undefined
    ):
        json = _modify_helper(name, position, permissions)

        if bitrate is not undefined:
            if bitrate is not None and not isinstance(bitrate, int):
                raise TypeError(
                    f'bitrate should be an int or None, got {bitrate.__class__.__name__!r}'
                )

            json['bitrate'] = bitrate

        if user_limit is not undefined:
            if user_limit is not None and not isinstance(user_limit, int):
                raise TypeError(
                    f'user_limit should be an int or None, got {user_limit.__class__.__name__!r}'
                )

            json['user_limit'] = user_limit

        if parent is not undefined:
            if parent is not None:
                json['parent_id'] = Snowflake.try_snowflake(parent)
            else:
                json['parent_id'] = None

        if rtc_origin is not undefined:
            if rtc_origin is not None and not isinstance(rtc_origin, str):
                raise TypeError(
                    f'rtc_origin should be a str or None, got {rtc_origin.__class__.__name__!r}'
                )

            json['rtc_origin'] = rtc_origin

        if video_quality_mode is not None:
            if video_quality_mode is not None and not isinstance(video_quality_mode, int):
                raise TypeError(
                    f'video_quality_mode should be an int or None, '
                    f'got {video_quality_mode.__class__.__name__!r}'
                )

            json['video_quality_mode'] = video_quality_mode

        data = await rest.modify_channel.request(
            self.state.client.rest, dict(channel_id=self.id), json=json
        )

        return self.state.upsert(data)


class DMChannel(BaseObject):
    last_message_id = JsonField('last_message_id', Snowflake)
    type = JsonField('type', ChannelType.get_enum)
    _recipients = JsonArray('recipients')

    async def close(self):
        return self.state.close(self.id)
