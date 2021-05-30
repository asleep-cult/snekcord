import enum

from .baseobject import BaseObject, BaseTemplate
from .. import rest
from ..utils import (JsonArray, JsonField, JsonTemplate, Snowflake,
                     _validate_keys)

__all__ = ('ChannelType', 'GuildChannel', 'TextChannel', 'VoiceChannel',
           'DMChannel')


class ChannelType(enum.IntEnum):
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
    @property
    def mention(self):
        return f'<#{self.id}>'

    @property
    def guild(self):
        return self.state.manager.guilds.get(self.guild_id)

    @property
    def parent(self):
        return self.state.manager.channels.get(self.parent_id)

    async def delete(self):
        await rest.delete_channel.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.id))

    async def modify(self, **kwargs):
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


TextChannelTemplate = JsonTemplate(
    topic=JsonField('topic'),
    slowmode=JsonField('rate_limit_per_user'),
    last_message_id=JsonField('last_message_id'),
    __extends__=(GuildChannelTemplate,)
)


class TextChannel(GuildChannel, template=TextChannelTemplate):
    __slots__ = ('messages',)

    def __init__(self, *, state):
        super().__init__(state=state)

        self.messages = self.state.manager.get_class('MessageState')(
            manager=self.state.manager, channel=self)

    async def typing(self):
        await rest.trigger_typing_indicator.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.id))

    async def pins(self):
        data = await rest.get_pinned_messages.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.id))

        return self.messages.upsert_many(data)


VoiceChannelTemplate = JsonTemplate(
    bitrate=JsonField('bitrate'),
    user_limit=JsonField('user_limit'),
    __extends__=(GuildChannelTemplate,)
)


class VoiceChannel(GuildChannel, template=VoiceChannelTemplate):
    pass


DMChannelTemplate = JsonTemplate(
    last_message_id=JsonField('last_message_id', Snowflake, str),
    type=JsonField('type'),
    _recipients=JsonArray('recipients'),
    __extends__=(BaseTemplate,)
)


class DMChannel(BaseObject, template=DMChannelTemplate):
    async def close(self):
        await rest.delete_channel.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.id))
