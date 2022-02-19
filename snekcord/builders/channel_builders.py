from __future__ import annotations

import typing

import attr

from .base_builders import AwaitableBuilder, setter
from ..rest.endpoints import CREATE_GUILD_CHANNEL
from ..snowflake import Snowflake

if typing.TYPE_CHECKING:
    from ..objects import BaseChannel, ChannelType
    from ..clients import Client
    from ..states import SupportsChannelID
else:
    BaseChannel = typing.NewType('BaseChannel', typing.Any)

__all__ = ('ChannelCreateBuilder',)


@attr.s()
class ChannelCreateBuilder(AwaitableBuilder[BaseChannel]):
    client: Client = attr.ib()
    guild_id: Snowflake = attr.ib()

    @setter
    def name(self, name: str) -> None:
        self.data['name'] = str(name)

    @setter
    def type(self, type: ChannelType) -> None:
        self.data['type'] = int(type)

    @setter
    def topic(self, topic: str) -> None:
        self.data['topic'] = str(topic)

    @setter
    def bitrate(self, bitrate: int) -> None:
        self.data['bitrate'] = int(bitrate)

    @setter
    def user_limit(self, user_limit: int) -> None:
        self.data['user_limit'] = int(user_limit)

    @setter
    def rate_limit_per_user(self, rate_limit_per_user: int) -> None:
        self.data['rate_limit_per_user'] = int(rate_limit_per_user)

    @setter
    def position(self, position: int) -> None:
        self.data['position'] = int(position)

    # TODO: permission overwrites

    @setter
    def parent(self, parent: SupportsChannelID) -> None:
        self.data['parent_id'] = self.client.channels.to_unique(parent)

    @setter
    def nsfw(self, nsfw: bool) -> None:
        self.data['nsfw'] = bool(nsfw)

    async def action(self) -> BaseChannel:
        data = await self.client.rest.request_api(
            CREATE_GUILD_CHANNEL, guild_id=self.guild_id, json=self.data
        )
        assert isinstance(data, dict)

        data['guild_id'] = self.guild_id
        return await self.client.channels.upsert(data)
