import enum

from .baseobject import BaseObject, BaseTemplate
from .. import rest
from ..utils import (JsonArray, JsonField, JsonTemplate, Snowflake,
                     _validate_keys)

__all__ = ('ChannelType', 'GuildChannel', 'TextChannel', 'VoiceChannel',
           'DMChannel')


class ChannelType(enum.IntEnum):
    """An enumaration of Discord's channel types

    | Name                   | Description                             |
    | ---------------------- | --------------------------------------- |
    | `GUILD_TEXT`           | A text channel in a `Guild`             |
    | `DM`                   | A direct message channel                |
    | `GUILD_VOICE`          | A voice channel in a `Guild`            |
    | `GROUP_DM`             | A `DM` channel with multiple recipients |
    | `GUILD_CATEGORY`       | A category channel in a `Guild`         |
    | `GUILD_NEWS`           | A news channel in a `Guild`             |
    | `GUILD_STORE`          | A store channel in a `Guild`            |
    | `GUILD_NEWS_THREAD`    | A news thread channel in a `Guild`      |
    | `GUILD_PUBLIC_THREAD`  | A public thread channel in a `Guild`    |
    | `GUILD_PRIVATE_THREAD` | A private thread channel in a `Guild`   |
    | `GUILD_STAGE_VOICE`    | A stage channel in a `Guild`            |
    """
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6
    GUILD_NEWS_THREAD = 10
    GUILD_PUBLIC_THREAD = 11
    GUILD_PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13


def _guild_channel_creation_keys(channel_type):
    channel_type = ChannelType(channel_type)
    keys = ('name', 'position', 'permission_overwrites')

    if channel_type in (ChannelType.GUILD_TEXT, ChannelType.GUILD_NEWS):
        keys += ('type', 'topic', 'nsfw')
    elif channel_type is ChannelType.GUILD_VOICE:
        keys += ('bitrate', 'userlimit')
    elif channel_type is channel_type.GUILD_STORE:
        keys += ('nsfw',)

    return keys


def _guild_channel_modification_keys(channel_type):
    channel_type = ChannelType(channel_type)
    keys = _guild_channel_creation_keys(channel_type)

    if channel_type is ChannelType.GUILD_VOICE:
        keys += ('rtc_region', 'video_quality_mode')

    return keys


GuildChannelTemplate = JsonTemplate(
    name=JsonField('name'),
    guild_id=JsonField('guild_id', Snowflake, str),
    _permission_overwrites=JsonArray('permission_overwrites'),
    position=JsonField('position'),
    nsfw=JsonField('nsfw'),
    parent_id=JsonField('parent_id'),
    type=JsonField('type'),
    __extends__=(BaseTemplate,)
)


class GuildChannel(BaseObject, template=GuildChannelTemplate):
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
        return self.state.manager.guilds.get(self.guild_id)

    @property
    def parent(self):
        """The channel's parent/category

        warning:
            This propery relies on the channel cache so it could return None
        """
        return self.state.manager.channels.get(self.parent_id)

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
        keys = _guild_channel_modification_keys(self.type)

        if self.type in (ChannelType.GUILD_TEXT, ChannelType.GUILD_NEWS,
                         ChannelType.GUILD_STORE):
            try:
                kwargs['parent_id'] = Snowflake.try_snowflake(
                    kwargs.pop('parent'))
            except KeyError:
                pass

        if self.type is ChannelType.GUILD_TEXT:
            try:
                kwargs['rate_limit_per_user'] = kwargs.pop('slowmode')
            except KeyError:
                pass

        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), keys)

        data = await rest.modify_channel.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.id),
            json=kwargs)

        return self.state.upsert(data)

    async def delete(self):
        """Invokes an API request to delete the channel"""
        await rest.delete_channel.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.id))


TextChannelTemplate = JsonTemplate(
    topic=JsonField('topic'),
    slowmode=JsonField('rate_limit_per_user'),
    last_message_id=JsonField('last_message_id'),
    __extends__=(GuildChannelTemplate,)
)


class TextChannel(GuildChannel, template=TextChannelTemplate):
    """Represents the `GUILD_TEXT` channel type

    Attributes:
        messages MessageState: The channel's message state

        topic str: The channel's topic

        slowmode int: The amount of time you have to wait between
            sending sucessive messages in the channel

        last_message_id Snowflake: The id of the last message sent in the
            channel
    """
    __slots__ = ('messages', 'last_pin_timestamp')

    def __init__(self, *, state):
        super().__init__(state=state)

        self.last_pin_timestamp = None

        self.messages = self.state.manager.get_class('MessageState')(
            manager=self.state.manager, channel=self)

    @property
    def last_message(self):
        """The last message sent in the channel

        warning:
            This property relies on the message cache so it could return None
        """
        return self.messages.get(self.last_message_id)

    async def typing(self):
        """Invokes an API request to trigger the typing indicator
        in the channel
        """
        await rest.trigger_typing_indicator.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.id))

    async def pins(self):
        """Invokes an API request to get the pinned messages
        in the channel

        Returns:
            list[Message]: The pinned messages in the channel
        """
        data = await rest.get_pinned_messages.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.id))

        return self.messages.upsert_many(data)


class CategoryChannel(GuildChannel):
    """Represents the `GUILD_CATEGORY` channel type"""
    def children(self):
        """Yields all of the `GuildChannels` that belong to this category"""
        for channel in self.state:
            if channel.parent_id == self.id:
                yield channel


VoiceChannelTemplate = JsonTemplate(
    bitrate=JsonField('bitrate'),
    user_limit=JsonField('user_limit'),
    __extends__=(GuildChannelTemplate,)
)


class VoiceChannel(GuildChannel, template=VoiceChannelTemplate):
    """Represents the `GUILD_VOICE` channel type

    Attributes:
        bitrate int: The channel's bitrate

        user_limit int: The maximum amount of people who can be in this
            channel at once
    """


DMChannelTemplate = JsonTemplate(
    last_message_id=JsonField('last_message_id', Snowflake, str),
    type=JsonField('type'),
    _recipients=JsonArray('recipients'),
    __extends__=(BaseTemplate,)
)


class DMChannel(BaseObject, template=DMChannelTemplate):
    async def close(self):
        """Invokes an API request to close the channel"""
        await rest.delete_channel.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.id))
