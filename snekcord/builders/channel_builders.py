from __future__ import annotations

import typing

import attr

from ..rest.endpoints import CREATE_GUILD_CHANNEL, UPDATE_GUILD_CHANNEL_POSITIONS
from ..snowflake import Snowflake
from ..undefined import MaybeUndefined, undefined
from .base_builders import AwaitableBuilder, setter

if typing.TYPE_CHECKING:
    from ..clients import Client
    from ..json import JSONObject
    from ..objects import BaseChannel, ChannelType
    from ..states import SupportsChannelID
else:
    BaseChannel = typing.NewType('BaseChannel', typing.Any)

__all__ = ('ChannelCreateBuilder', 'ChannelPositionsBuilder')


@attr.s(kw_only=True)
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

        return await self.client.channels.upsert(
            self.client.channels.inject_metadata(data, self.guild_id)
        )


@attr.s(kw_only=True)
class ChannelPositionsBuilder(AwaitableBuilder[None]):
    client: Client = attr.ib()
    guild_id: Snowflake = attr.ib()

    @setter
    def set(
        self,
        channel: SupportsChannelID,
        *,
        position: MaybeUndefined[typing.Optional[int]] = undefined,
        lock_permissions: MaybeUndefined[typing.Optional[bool]] = undefined,
        parent: MaybeUndefined[typing.Optional[SupportsChannelID]] = undefined,
    ) -> None:
        channel_id = str(self.client.channels.to_unique(channel))

        data: JSONObject = {'id': channel_id}

        if position is not undefined:
            if position is not None:
                data['position'] = int(position)
            else:
                data['position'] = None

        if lock_permissions is not undefined:
            if lock_permissions is not None:
                data['lock_permissions'] = bool(lock_permissions)
            else:
                data['lock_permissions'] = None

        if parent is not undefined:
            if parent is not None:
                data['parent_id'] = str(self.client.channels.to_unique(parent))
            else:
                data['parent_id'] = None

        self.data[channel_id] = data

    async def action(self) -> None:
        json = list(self.data.values())

        await self.client.rest.request_api(
            UPDATE_GUILD_CHANNEL_POSITIONS, guild_id=self.guild_id, json=json
        )
