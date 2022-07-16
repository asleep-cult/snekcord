from __future__ import annotations

import enum
import typing

from ..enums import convert_enum
from ..exceptions import UnsupportedDataError
from ..rest.endpoints import (
    CREATE_GUILD_CHANNEL,
    DELETE_CHANNEL,
    GET_CHANNEL,
    GET_GUILD_CHANNELS,
    TRIGGER_CHANNEL_TYPING,
    UPDATE_CHANNEL,
    UPDATE_GUILD_CHANNEL_POSITIONS,
)
from ..snowflake import Snowflake
from ..undefined import undefined
from .bases import BaseAPI

if typing.TYPE_CHECKING:
    from typing_extensions import NotRequired

    from ..json import JSONObject
    from ..websockets import Shard

ThreadAutoArchiveDuration = typing.Literal[60, 1440, 4320, 10080]
VideoQualityMode = typing.Literal[1, 2]


class OverwriteType(enum.IntEnum):
    ROLE = 0
    MEMBER = 1


class RawOverwrite(typing.TypedDict):
    id: Snowflake
    type: typing.Union[OverwriteType, int]
    allow: int
    deny: int


class ChannelType(enum.IntEnum):
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_NEWS_THREAD = 10
    GUILD_PUBLIC_THREAD = 11
    GUILD_PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13
    GUILD_DIRECTORY = 14
    GUILD_FORUM = 15


class RawChannel(typing.TypedDict):
    id: Snowflake
    type: typing.Union[ChannelType, int]
    name: str


class _BaseChannel(typing.TypedDict):
    id: Snowflake
    name: str


class RawGuildChannel(_BaseChannel):
    guild_id: Snowflake
    position: int
    permission_overwrites: typing.List[RawOverwrite]


class RawCategoryChannel(RawGuildChannel):
    type: typing.Literal[ChannelType.GUILD_CATEGORY]


class RawTextChannel(RawGuildChannel):
    type: typing.Literal[ChannelType.GUILD_TEXT]
    parent_id: typing.Optional[Snowflake]
    topic: typing.Optional[str]
    nsfw: NotRequired[bool]
    last_message_id: typing.Optional[Snowflake]
    rate_limit_per_user: int
    last_pin_timestamp: NotRequired[typing.Optional[str]]
    default_auto_archive_duration: NotRequired[ThreadAutoArchiveDuration]


class VideoQualityMore(enum.IntEnum):
    AUTO = 1
    FULL = 2


class RawVoiceChannel(RawGuildChannel):
    type: typing.Literal[ChannelType.GUILD_VOICE]
    parent_id: typing.Optional[Snowflake]
    nsfw: NotRequired[bool]
    bitrate: int
    user_limit: int
    rtc_region: typing.Optional[int]
    video_quality_mode: NotRequired[VideoQualityMode]


RawChannelTypes = typing.Union[
    RawChannel,
    RawCategoryChannel,
    RawTextChannel,
    RawVoiceChannel,
]


RawChannelCreate = RawChannelTypes
RawChannelUpdate = RawChannelTypes
RawChannelDelete = RawChannelTypes


class RawChannelPinsUpdate(typing.TypedDict):
    guild_id: NotRequired[Snowflake]
    channel_id: Snowflake
    last_pin_timestamp: NotRequired[typing.Optional[str]]


class ChannelAPI(BaseAPI):
    def sanitize_overwrite(self, data: JSONObject) -> RawOverwrite:
        return {
            'id': Snowflake(data['id']),
            'type': convert_enum(OverwriteType, data['type']),
            'allow': int(data['allow']),
            'deny': int(data['deny']),
        }

    def sanitize_channel(
        self, data: JSONObject, *, guild_id: typing.Optional[Snowflake] = None
    ) -> RawChannelTypes:
        type = convert_enum(ChannelType, data['type'])

        if guild_id is not None:
            data['guild_id'] = guild_id

        if type is ChannelType.GUILD_CATEGORY:
            overwrites = data['permission_overwrites']

            return {
                'id': Snowflake(data['id']),
                'type': ChannelType.GUILD_CATEGORY,
                'name': data['name'],
                'guild_id': Snowflake(data['guild_id']),
                'position': data['position'],
                'permission_overwrites': [self.sanitize_overwrite(ov) for ov in overwrites],
            }

        elif type is ChannelType.GUILD_TEXT:
            parent_id = data['parent_id']
            if parent_id is not None:
                parent_id = Snowflake(parent_id)

            overwrites = data['permission_overwrites']

            last_message_id = data['last_message_id']
            if last_message_id is not None:
                last_message_id = Snowflake(last_message_id)

            text_channel: RawTextChannel = {
                'id': Snowflake(data['id']),
                'type': ChannelType.GUILD_TEXT,
                'name': data['name'],
                'guild_id': Snowflake(data['guild_id']),
                'position': data['position'],
                'parent_id': Snowflake(parent_id) if parent_id is not None else None,
                'permission_overwrites': [self.sanitize_overwrite(ov) for ov in overwrites],
                'topic': data['topic'],
                'last_message_id': last_message_id,
                'rate_limit_per_user': data['rate_limit_per_user'],
            }

            nsfw = data.get('nsfw')
            if nsfw is not None:
                text_channel['nsfw'] = nsfw

            last_pin_timestamp = data.get('last_pin_timestamp', undefined)
            if last_pin_timestamp is not undefined:
                text_channel['last_pin_timestamp'] = last_pin_timestamp

            default_auto_archive_duration = data.get('default_auto_archive_duration')
            if default_auto_archive_duration is not None:
                text_channel['default_auto_archive_duration'] = default_auto_archive_duration

            return text_channel

        elif type is ChannelType.GUILD_VOICE:
            parent_id = data['parent_id']
            if parent_id is not None:
                parent_id = Snowflake(parent_id)

            overwrites = data['permission_overwrites']

            voice_channel: RawVoiceChannel = {
                'id': Snowflake(data['id']),
                'type': ChannelType.GUILD_VOICE,
                'name': data['name'],
                'guild_id': Snowflake(data['guild_id']),
                'position': data['position'],
                'parent_id': parent_id,
                'permission_overwrites': [self.sanitize_overwrite(ov) for ov in overwrites],
                'bitrate': data['bitrate'],
                'user_limit': data['user_limit'],
                'rtc_region': data['rtc_region'],
            }

            nsfw = data.get('nsfw')
            if nsfw is not None:
                voice_channel['nsfw'] = nsfw

            video_quality_mode = data.get('video_quality_mode')
            if video_quality_mode is not None:
                voice_channel['video_quality_mode'] = video_quality_mode

            return voice_channel

        return {
            'id': Snowflake(data['id']),
            'type': convert_enum(ChannelType, data['type']),
            'name': data['name'],
        }

    def sanitize_pins_update(self, data: JSONObject) -> RawChannelPinsUpdate:
        pins_update: RawChannelPinsUpdate = {'channel_id': Snowflake(data['channel_id'])}

        guild_id = data.get('guild_id')
        if guild_id is not None:
            pins_update['guild_id'] = Snowflake(guild_id)

        last_pin_timestamp = data.get('last_pin_timestamp', undefined)
        if last_pin_timestamp is not undefined:
            pins_update['last_pin_timestamp'] = last_pin_timestamp

        return pins_update

    async def on_channel_create(self, shard: Shard, data: JSONObject) -> None:
        channel = self.sanitize_channel(data)
        await self.client.channels.channel_created(shard, channel)

    async def on_channel_update(self, shard: Shard, data: JSONObject) -> None:
        channel = self.sanitize_channel(data)
        await self.client.channels.channel_updated(shard, channel)

    async def on_channel_delete(self, shard: Shard, data: JSONObject) -> None:
        channel = self.sanitize_channel(data)
        await self.client.channels.channel_deleted(shard, channel)

    async def on_channel_pins_update(self, shard: Shard, data: JSONObject) -> None:
        pins_update = self.sanitize_pins_update(data)
        await self.client.channels.channel_pins_updated(shard, pins_update)

    async def get_channel(self, channel_id: Snowflake) -> RawChannelTypes:
        data = await self.request_api(GET_CHANNEL, channel_id=channel_id)

        if not isinstance(data, dict):
            raise UnsupportedDataError(self.client.rest, data)

        return self.sanitize_channel(data)

    async def get_guild_channels(self, guild_id: Snowflake) -> typing.List[RawChannelTypes]:
        channels = await self.request_api(GET_GUILD_CHANNELS, guild_id=guild_id)

        if not isinstance(channels, list):
            raise UnsupportedDataError(self.client.rest, channels)

        return [self.sanitize_channel(channel, guild_id=guild_id) for channel in channels]

    async def create_guild_channel(
        self,
        guild_id: Snowflake,
        json: JSONObject,
        *,
        autit_log_reason: typing.Optional[str] = None,
    ) -> RawChannelTypes:
        data = await self.request_api(
            CREATE_GUILD_CHANNEL, guild_id=guild_id, json=json, autit_log_reason=autit_log_reason
        )

        if not isinstance(data, dict):
            raise UnsupportedDataError(self.client.rest, data)

        return self.sanitize_channel(data, guild_id=guild_id)

    async def update_channel(
        self,
        channel_id: Snowflake,
        json: JSONObject,
        *,
        autit_log_reason: typing.Optional[str] = None,
    ) -> RawChannelTypes:
        data = await self.request_api(
            UPDATE_CHANNEL, channel_id=channel_id, json=json, autit_log_reason=autit_log_reason
        )

        if not isinstance(data, dict):
            raise UnsupportedDataError(self.client.rest, data)

        return self.sanitize_channel(data)

    async def update_channel_positions(
        self, guild_id: Snowflake, json: typing.List[JSONObject]
    ) -> None:
        await self.request_api(UPDATE_GUILD_CHANNEL_POSITIONS, guild_id=guild_id, json=json)

    async def delete_channel(
        self, channel_id: Snowflake, *, autit_log_reason: typing.Optional[str] = None
    ) -> RawChannelTypes:
        data = await self.request_api(
            DELETE_CHANNEL, channel_id=channel_id, autit_log_reason=autit_log_reason
        )

        if not isinstance(data, dict):
            raise UnsupportedDataError(self.client.rest, data)

        return self.sanitize_channel(data)

    async def trigger_channel_typing(self, channel_id: Snowflake) -> None:
        await self.request_api(TRIGGER_CHANNEL_TYPING, channel_id=channel_id)
