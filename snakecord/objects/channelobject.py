import enum

from .baseobject import BaseObject
from .. import rest
from ..templates import (DMChannelTemplate, GuildChannelTemplate,
                         TextChannelTemplate, VoiceChannelTemplate)
from ..utils import Snowflake, _validate_keys


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


class GuildChannel(BaseObject, template=GuildChannelTemplate):
    __slots__ = ('guild',)

    def __init__(self, *, state, guild):
        super().__init__(state=state)
        self.guild = guild

    @property
    def mention(self):
        return f'<#{self.id}>'

    async def delete(self):
        await rest.delete_channel.request(
            session=self._state.manager.rest,
            fmt=dict(channel_id=self.id))

    async def modify(self, **kwargs):
        keys = _guild_channel_modification_keys(self.type)

        if self.type in (ChannelType.GUILD_TEXT, ChannelType.GUILD_NEWS,
                         ChannelType.GUILD_STORE):
            try:
                kwargs['parent_id'] = (
                    Snowflake.try_snowflake(kwargs.pop('parent'))
                )
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
            session=self._state.manager.rest,
            fmt=dict(channel_id=self.id),
            json=kwargs)

        return self._state.append(data)


class TextChannel(GuildChannel, template=TextChannelTemplate):
    pass


class VoiceChannel(GuildChannel, template=VoiceChannelTemplate):
    pass


class DMChannel(BaseObject, template=DMChannelTemplate):
    async def close(self):
        await rest.delete_channel.request(
            session=self._state.manager.rest,
            fmt=dict(channel_id=self.id))
