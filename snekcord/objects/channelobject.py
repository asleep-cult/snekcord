from __future__ import annotations

import typing as t

from .baseobject import BaseObject, BaseTemplate
from .. import rest
from ..utils import (Enum, JsonArray, JsonField, JsonObject, JsonTemplate,
                     Snowflake, _validate_keys)

__all__ = ('ChannelType', 'GuildChannel', 'TextChannel', 'FollowedChannel',
           'CategoryChannel', 'VoiceChannel', 'DMChannel')

if t.TYPE_CHECKING:
    from ..objects import Guild, Message
    from ..states.channelstate import ChannelState
    from ..states.messagestate import MessageState
    from ..states.overwritestate import PermissionOverwriteState
    from ..typing import Json, SnowflakeType


class ChannelType(Enum[int]):
    """An enumeration of Discord's channel types

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


def _guild_channel_creation_keys(
    channel_type: ChannelType
) -> t.Tuple[str, ...]:
    keys: t.Tuple[str, ...] = ('name', 'position', 'permission_overwrites')

    if channel_type in (ChannelType.GUILD_TEXT, ChannelType.GUILD_NEWS):
        keys += ('type', 'topic', 'nsfw')
    elif channel_type == ChannelType.GUILD_VOICE:
        keys += ('bitrate', 'userlimit')
    elif channel_type == ChannelType.GUILD_STORE:
        keys += ('nsfw',)

    return keys


def _guild_channel_modification_keys(
    channel_type: ChannelType
) -> t.Tuple[str, ...]:
    keys = _guild_channel_creation_keys(channel_type)

    if channel_type == ChannelType.GUILD_VOICE:
        keys += ('rtc_region', 'video_quality_mode')

    return keys


GuildChannelTemplate = JsonTemplate(
    name=JsonField('name'),
    guild_id=JsonField('guild_id', Snowflake, str),
    position=JsonField('position'),
    nsfw=JsonField('nsfw'),
    parent_id=JsonField('parent_id', Snowflake, str),
    type=JsonField('type', ChannelType.get_enum, ChannelType.get_value),
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
    __slots__ = ('permissions',)

    if t.TYPE_CHECKING:
        name: str
        guild_id: Snowflake
        parent_id: t.Optional[Snowflake]
        state: ChannelState
        type: ChannelType
        permissions: PermissionOverwriteState

    def __init__(self, *, state: ChannelState):
        super().__init__(state=state)

        cls = self.state.client.get_class(  # type: ignore
            'PermissionOverwriteState')
        self.permissions = cls(  # type: ignore
            client=self.state.client, channel=self)

    @property
    def mention(self):
        """The channel in mention format, equivalent to `f'<#{self.id}>'`"""
        return f'<#{self.id}>'

    @property
    def guild(self) -> t.Optional[Guild]:
        """The `Guild` that the channel belongs to

        warning:
            This propery relies on the guild cache so it could return None
        """
        return self.state.client.guilds.get(self.guild_id)

    @property
    def parent(self) -> t.Optional[CategoryChannel]:
        """The channel's parent/category

        warning:
            This propery relies on the channel cache so it could return None
        """
        return self.state.client.channels.get(self.parent_id)  # type: ignore

    async def modify(self, **kwargs: t.Any) -> GuildChannel:
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

        _validate_keys(f'{self.__class__.__name__}.modify',  # type: ignore
                       kwargs, (), _guild_channel_modification_keys(self.type))

        data = await rest.modify_channel.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.id),
            json=kwargs)

        return self.state.upsert(data)  # type: ignore

    async def delete(self) -> None:
        """Invokes an API request to delete the channel"""
        await rest.delete_channel.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.id))

    def update(  # type: ignore
        self, data: Json, *args: t.Any, **kwargs: t.Any
    ) -> None:
        super().update(data, *args, **kwargs)

        guild = self.guild
        if guild is not None:
            guild.channels.add_key(self.id)

        permission_overwrites = data.get('permission_overwrites')
        if permission_overwrites is not None:
            self.permissions.upsert_replace(permission_overwrites)


FollowedChannelTemplate = JsonTemplate(
    channel_id=JsonField('channel_id', Snowflake, str),
    webhook_id=JsonField('webhook_id', Snowflake, str),
)


class FollowedChannel(JsonObject, template=FollowedChannelTemplate):
    def __init__(self, *, state):
        self.state = state

    @property
    def channel(self):
        return self.state.get(self.channel_id)


TextChannelTemplate = JsonTemplate(
    topic=JsonField('topic'),
    slowmode=JsonField('rate_limit_per_user'),
    last_message_id=JsonField('last_message_id', Snowflake, str),
    __extends__=(GuildChannelTemplate,)
)


class TextChannel(GuildChannel, template=TextChannelTemplate):
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

    if t.TYPE_CHECKING:
        messages: MessageState
        last_message_id: Snowflake

    def __init__(self, *, state: ChannelState):
        super().__init__(state=state)

        self.last_pin_timestamp = None

        self.messages = self.state.client.get_class(
            'MessageState')(  # type: ignore
            client=self.state.client, channel=self)  # type: ignore

    def __str__(self):
        return f'#{self.name}'

    @property
    def last_message(self) -> t.Optional[Message]:
        """The last message sent in the channel

        warning:
            This property relies on the message cache so it could return None
        """
        return self.messages.get(self.last_message_id)

    async def follow(self, webhook_channel: SnowflakeType) -> FollowedChannel:
        webhook_channel_id = Snowflake.try_snowflake(webhook_channel)

        data = await rest.follow_news_channel.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.id),
            params=dict(webhook_channel_id=webhook_channel_id))

        return FollowedChannel.unmarshal(data, state=self.state)

    async def typing(self) -> None:
        """Invokes an API request to trigger the typing indicator
        in the channel
        """
        await rest.trigger_typing_indicator.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.id))

    async def fetch_pins(self) -> t.Set[Message]:
        """Invokes an API request to get the pinned messages
        in the channel

        Returns:
            list[Message]: The pinned messages in the channel
        """
        data = await rest.get_pinned_messages.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.id))

        return self.messages.upsert_many(data)


class CategoryChannel(GuildChannel, template=GuildChannelTemplate):
    """Represents the `GUILD_CATEGORY` channel type"""
    def __str__(self):
        return f'#{self.name}'

    @property
    def children(self) -> t.Generator[GuildChannel, None, None]:
        """Yields all of the `GuildChannels` that belong to this category"""
        if self.guild is not None:
            for channel in self.guild.channels:
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
    if t.TYPE_CHECKING:
        bitrate: int
        user_limit: t.Optional[int]

    def __str__(self) -> str:
        return f'#!{self.name}'


DMChannelTemplate = JsonTemplate(
    last_message_id=JsonField('last_message_id', Snowflake, str),
    type=JsonField(
        'type',
        ChannelType.get_enum,
        ChannelType.get_value
    ),
    _recipients=JsonArray('recipients'),
    __extends__=(BaseTemplate,)
)


class DMChannel(BaseObject, template=DMChannelTemplate):
    if t.TYPE_CHECKING:
        type: ChannelType

    async def close(self) -> None:
        """Invokes an API request to close the channel"""
        await rest.delete_channel.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.id))
