from .baseobject import BaseObject
from .. import rest
from ..clients.client import ClientClasses
from ..enums import ChannelType
from ..utils import JsonArray, JsonField, Snowflake, undefined


def _modify_helper(name, position, permission):
    json = {}

    if name is not None:
        json['name'] = str(name)

    if position is not undefined:
        if position is not None:
            json['position'] = int(position)
        else:
            json['position'] = None

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

    def _delete(self):
        super()._delete()
        guild = self.guild
        if guild is not None:
            guild.channels.remove_key(self.id)

    def update(self, data, *args, **kwargs):
        super().update(data, *args, **kwargs)

        guild = self.guild
        if guild is not None:
            guild.channels.add_key(self.id)

        permission_overwrites = data.get('permission_overwrites')
        if permission_overwrites is not None:
            overwrites = set()

            for overwrite in permission_overwrites:
                overwrites.add(self.permissions.upsert(overwrite).id)

            for overwrite_id in set(self.permissions.keys()) - overwrites:
                del self.permissions.mapping[overwrite_id]


class TextChannel(GuildChannel):
    __slots__ = ('last_pin_timestamp', 'messages', 'pins')

    topic = JsonField('topic')
    slowmode = JsonField('rate_limit_per_user')
    last_message_id = JsonField('last_message_id', Snowflake)

    def __init__(self, *, state):
        super().__init__(state=state)

        self.last_pin_timestamp = None
        self.messages = ClientClasses.MessageState(client=self.state.client, channel=self)
        self.pins = ClientClasses.ChannelPinsState(superstate=self.messages, channel=self)

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
            if topic is not None:
                json['topic'] = str(topic)
            else:
                json['topic'] = None

        if nsfw is not undefined:
            if nsfw is not None:
                json['nsfw'] = bool(nsfw)
            else:
                json['nsfw'] = None

        if slowmode is not undefined:
            if slowmode is not None:
                json['slowmode'] = int(slowmode)
            else:
                json['slowmode'] = None

        if parent is not undefined:
            if parent is not None:
                json['parent_id'] = Snowflake.try_snowflake(parent)
            else:
                json['parent_id'] = None

        if thread_archive_duration is not undefined:
            if thread_archive_duration is not None:
                json['default_auto_archive_duration'] = int(thread_archive_duration)
            else:
                json['default_auto_archive_duration'] = None

        data = await rest.modify_channel.request(
            self.state.client.rest, {'channel_id': self.id}, json=json
        )

        return self.state.upsert(data)

    async def add_follower(self, channel):
        channel_id = Snowflake.try_snowflake(channel)

        data = await rest.follow_news_channel.request(
            self.state.client.rest, {'channel_id': self.id},
            params={'webhook_channel_id': channel_id}
        )

        return Snowflake(data['webhook_id'])

    async def typing(self):
        await rest.trigger_typing_indicator.request(
            self.state.client.rest, {'channel_id': self.id}
        )


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
            self.state.client.rest, {'channel_id': self.id}, json=json
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
            if bitrate is not None:
                json['bitrate'] = int(bitrate)
            else:
                json['birtate'] = None

        if user_limit is not undefined:
            if user_limit is not None:
                json['user_limit'] = int(user_limit)
            else:
                json['user_limit'] = None

        if parent is not undefined:
            if parent is not None:
                json['parent_id'] = Snowflake.try_snowflake(parent)
            else:
                json['parent_id'] = None

        if rtc_origin is not undefined:
            if rtc_origin is not None:
                json['rtc_origin'] = str(rtc_origin)
            else:
                json['rtc_origin'] = None

        if video_quality_mode is not None:
            if video_quality_mode is not None:
                json['video_quality_mode'] = int(video_quality_mode)
            else:
                json['video_quality_mode'] = None

        data = await rest.modify_channel.request(
            self.state.client.rest, {'channel_id': self.id}, json=json
        )

        return self.state.upsert(data)


class DMChannel(BaseObject):
    last_message_id = JsonField('last_message_id', Snowflake)
    type = JsonField('type', ChannelType.get_enum)
    _recipients = JsonArray('recipients')

    async def close(self):
        return self.state.close(self.id)
