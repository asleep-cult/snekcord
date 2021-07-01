from .baseobject import BaseObject
from .. import rest
from ..clients.client import ClientClasses
from ..enums import ChannelType
from ..utils import JsonArray, JsonField, JsonObject, Snowflake, _validate_keys

__all__ = ('GuildChannel', 'TextChannel', 'FollowedChannel', 'CategoryChannel',
           'VoiceChannel', 'DMChannel')


def _guild_channel_creation_keys(channel_type):
    keys = ('name', 'position', 'permission_overwrites')

    if channel_type in (ChannelType.GUILD_TEXT, ChannelType.GUILD_NEWS):
        keys += ('type', 'topic', 'nsfw')
    elif channel_type == ChannelType.GUILD_VOICE:
        keys += ('bitrate', 'userlimit')
    elif channel_type == ChannelType.GUILD_STORE:
        keys += ('nsfw',)

    return keys


def _guild_channel_modification_keys(channel_type):
    keys = _guild_channel_creation_keys(channel_type)

    if channel_type == ChannelType.GUILD_VOICE:
        keys += ('rtc_region', 'video_quality_mode')

    return keys


class GuildChannel(BaseObject):
    """The base class for all channels that belong to a `Guild`

    Attributes:
        name str: The channel's name

        guild_id Snowflake: The id of the guild that the channel belongs to

        position int: The channel's position

        nsfw bool: `True` if the channel is allowed to have explicit content
            otherwise `False`

        parent_id Snowflake: The id of the channel's parent/category

        type ChannelType: The channel's type
    """
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
            client=self.state.client, channel=self)

    @property
    def mention(self):
        """The channel in mention format, equivalent to `f'<#{self.id}>'`"""
        return f'<#{self.id}>'

    @property
    def guild(self):
        """The `Guild` that the channel belongs to

        warning:
            This propery relies on the guild cache so it could return None
        """
        return self.state.client.guilds.get(self.guild_id)

    @property
    def parent(self):
        """The channel's parent/category

        warning:
            This propery relies on the channel cache so it could return None
        """
        return self.state.client.channels.get(self.parent_id)

    async def modify(self, **kwargs):
        """Invokes an API request to modify the channel

        **Arguments:**

        | Name         | Type            | Channel Types                                            |
        | ------------ | --------------- | -------------------------------------------------------- |
        | `name`       | `str`           | `All`                                                    |
        | `type`       | `ChannelType`   | `GUILD_TEXT`, `GUILD_NEWS`                               |
        | `position`   | `int`           | `All`                                                    |
        | `topic`      | `str`           | `GUILD_TEXT`, `GUILD_NEWS`                               |
        | `nsfw`       | `bool`          | `GUILD_TEXT`, `GUILD_NEWS`, `GUILD_STORE`                |
        | `slowmode`   | `int`           | `GUILD_TEXT`                                             |
        | `bitrate`    | `int`           | `GUILD_VOICE`                                            |
        | `user_limit` | `int`           | `GUILD_VOICE`                                            |
        | `parent`     | `SnowflakeLike` | `GUILD_TEXT`, `GUILD_NEWS`, `GUILD_STORE`, `GUILD_VOICE` |
        | `rtc_region` | `str`           | `GUILD_VOICE`                                            |

        note:
            Discord only supports conversion between `GUILD_TEXT` and `GUILD_NEWS`
            channel types

        Returns:
            GuildChannel: The modified channel
        """  # noqa: E501
        if self.type in (ChannelType.GUILD_TEXT, ChannelType.GUILD_NEWS,
                         ChannelType.GUILD_STORE):
            try:
                kwargs['parent_id'] = Snowflake.try_snowflake(
                    kwargs.pop('parent'))
            except KeyError:
                pass

        if self.type == ChannelType.GUILD_TEXT:
            try:
                kwargs['rate_limit_per_user'] = kwargs.pop('slowmode')
            except KeyError:
                pass

        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), _guild_channel_modification_keys(self.type))

        data = await rest.modify_channel.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.id),
            json=kwargs)

        return self.state.upsert(data)

    async def delete(self):
        """Invokes an API request to delete the channel"""
        await rest.delete_channel.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.id))

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


class FollowedChannel(JsonObject):
    channel_id = JsonField('channel_id', Snowflake)
    webhook_id = JsonField('webhook_id', Snowflake)

    def __init__(self, *, state):
        self.state = state

    @property
    def channel(self):
        return self.state.get(self.channel_id)


class TextChannel(GuildChannel):
    """Represents the `GUILD_TEXT` and `GUILD_NEWS` channel types

    Attributes:
        messages MessageState: The channel's message state

        topic str: The channel's topic

        slowmode int: The amount of time you have to wait between
            sending sucessive messages in the channel

        last_message_id Snowflake: The id of the last message sent in the
            channel
    """
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

    @property
    def last_message(self):
        """The last message sent in the channel

        warning:
            This property relies on the message cache so it could return None
        """
        return self.messages.get(self.last_message_id)

    async def follow(self, webhook_channel):
        webhook_channel_id = Snowflake.try_snowflake(webhook_channel)

        data = await rest.follow_news_channel.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.id),
            params=dict(webhook_channel_id=webhook_channel_id))

        return FollowedChannel.unmarshal(data, state=self.state)

    async def typing(self):
        """Invokes an API request to trigger the typing indicator
        in the channel
        """
        await rest.trigger_typing_indicator.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.id))

    async def fetch_pins(self):
        """Invokes an API request to get the pinned messages
        in the channel

        Returns:
            list[Message]: The pinned messages in the channel
        """
        data = await rest.get_pinned_messages.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.id))

        messages = []

        for message in data:
            messages.append(self.messages.upsert(message))

        return messages


class CategoryChannel(GuildChannel):
    """Represents the `GUILD_CATEGORY` channel type"""
    def __str__(self):
        return f'#{self.name}'

    @property
    def children(self):
        """Yields all of the `GuildChannels` that belong to this category"""
        if self.guild is not None:
            for channel in self.guild.channels:
                if channel.parent_id == self.id:
                    yield channel


class VoiceChannel(GuildChannel):
    """Represents the `GUILD_VOICE` channel type

    Attributes:
        bitrate int: The channel's bitrate

        user_limit int: The maximum amount of people who can be in this
            channel at once
    """
    bitrate = JsonField('bitrate')
    user_limit = JsonField('user_limit')

    def __str__(self):
        return f'#!{self.name}'


class DMChannel(BaseObject):
    last_message_id = JsonField('last_message_id', Snowflake)
    type = JsonField('type', ChannelType.get_enum)
    _recipients = JsonArray('recipients')

    async def close(self):
        """Invokes an API request to close the channel"""
        await rest.delete_channel.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.id))
