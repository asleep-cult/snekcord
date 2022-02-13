from __future__ import annotations

import typing

import attr

from .base_builders import AwaitableBuilder, setter
from ..rest.endpoints import CREATE_GUILD_CHANNEL
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined, undefined

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
    def name(self, name: MaybeUndefined[str]) -> None:
        if name is not undefined:
            self.data['name'] = str(name)

    @setter
    def type(self, type: MaybeUndefined[ChannelType]) -> None:
        if type is not undefined:
            self.data['type'] = int(type)

    @setter
    def topic(self, topic: MaybeUndefined[str]) -> None:
        if topic is not undefined:
            self.data['topic'] = str(topic)

    @setter
    def bitrate(self, bitrate: MaybeUndefined[int]) -> None:
        if bitrate is not undefined:
            self.data['bitrate'] = int(bitrate)

    @setter
    def user_limit(self, user_limit: MaybeUndefined[int]) -> None:
        if user_limit is not undefined:
            self.data['user_limit'] = int(user_limit)

    @setter
    def rate_limit_per_user(self, rate_limit_per_user: MaybeUndefined[int]) -> None:
        if rate_limit_per_user is not undefined:
            self.data['rate_limit_per_user'] = int(rate_limit_per_user)

    @setter
    def position(self, position: MaybeUndefined[int]) -> None:
        if position is not undefined:
            self.data['position'] = position

    # TODO: permission overwrites

    @setter
    def parent(self, parent: MaybeUndefined[SupportsChannelID]) -> None:
        if parent is not undefined:
            self.data['parent_id'] = self.client.channels.to_unique(parent)

    @setter
    def nsfw(self, nsfw: MaybeUndefined[bool]) -> None:
        if nsfw is not undefined:
            self.data['nsfw'] = bool(nsfw)

    async def action(self) -> BaseChannel:
        data = await self.client.rest.request_api(
            CREATE_GUILD_CHANNEL, guild_id=self.guild_id, json=self.data
        )
        assert isinstance(data, dict)

        data['guild_id'] = self.guild_id
        return await self.client.channels.upsert(data)
