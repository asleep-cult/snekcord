from __future__ import annotations

import typing

import attr

from ..snowflake import Snowflake
from ..undefined import MaybeUndefined, undefined
from .base_builders import AwaitableBuilder, setter

if typing.TYPE_CHECKING:
    from typing_extensions import NotRequired

    from ..clients import Client
    from ..json import JSONObject
    from ..objects import Channel, ChannelType, SupportsChannelID

__all__ = ('ChannelCreateSetters', 'ChannelCreateBuilder', 'ChannelPositionsBuilder')


class ChannelCreateSetters(typing.TypedDict):
    name: NotRequired[str]
    type: NotRequired[ChannelType]
    topic: NotRequired[str]
    bitrate: NotRequired[int]
    user_limit: NotRequired[int]
    rate_limit_per_user: NotRequired[int]
    position: NotRequired[int]
    parent: NotRequired[SupportsChannelID]
    nsfw: NotRequired[bool]


@attr.s(kw_only=True)
class ChannelCreateBuilder(AwaitableBuilder):
    """A builder for the CREATE_GUILD_CHANNEL endpoint."""

    client: Client = attr.ib()
    guild_id: Snowflake = attr.ib()

    data: JSONObject = attr.ib(init=False, factory=dict)

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

    async def action(self) -> Channel:
        data = await self.client.channels.api.create_guild_channel(self.guild_id, self.data)
        return await self.client.channels.upsert(data)


@attr.s(kw_only=True)
class ChannelPositionsBuilder(AwaitableBuilder):
    """A builder for the UPDATE_GUILD_CHANNEL_POSITIONS endpoint."""

    client: Client = attr.ib()
    guild_id: Snowflake = attr.ib()

    channels: typing.List[JSONObject] = attr.ib(init=False, factory=list)

    @setter
    def set(
        self,
        channel: SupportsChannelID,
        *,
        position: MaybeUndefined[typing.Optional[int]] = undefined,
        lock_permissions: MaybeUndefined[typing.Optional[bool]] = undefined,
        parent: MaybeUndefined[typing.Optional[SupportsChannelID]] = undefined,
    ) -> None:
        data: JSONObject = {}

        if position is not undefined:
            if position is not None:
                data['position'] = int(position)
            else:
                data['position'] = None

        if lock_permissions is not undefined:
            if lock_permissions is not None:
                data['lock_permissions'] = lock_permissions
            else:
                data['lock_permissions'] = None

        if parent is not undefined:
            if parent is not None:
                data['parent_id'] = str(self.client.channels.to_unique(parent))
            else:
                data['parent_id'] = None

        data['id'] = str(self.client.channels.to_unique(channel))
        self.channels.append(data)

    async def action(self) -> None:
        await self.client.channels.api.update_channel_positions(
            guild_id=self.guild_id, json=self.channels
        )
