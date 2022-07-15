from __future__ import annotations

import typing
from datetime import datetime

import attr

from ..cache import CachedModel
from ..exceptions import UnknownMemberError
from ..snowflake import Snowflake, SnowflakeCouple
from ..undefined import MaybeUndefined
from .base import BaseObject, SnowflakeWrapper

if typing.TYPE_CHECKING:
    from ..clients import Client
    from ..states import MemberState
    from .guild import GuildIDWrapper, SupportsGuildID
    from .user import SupportsUserID, UserIDWrapper

__all__ = ('CachedMember', 'Member', 'SupportsMemberID', 'MemberIDWrapper')


class CachedMember(CachedModel):
    user_id: Snowflake
    guild_id: Snowflake
    nick: MaybeUndefined[typing.Optional[str]]
    avatar: MaybeUndefined[typing.Optional[str]]
    role_ids: typing.List[str]
    joined_at: str
    premium_since: MaybeUndefined[typing.Optional[str]]
    deaf: bool
    mute: bool
    pending: MaybeUndefined[bool]
    communication_disabled_until: MaybeUndefined[typing.Optional[int]]


@attr.s(kw_only=True)
class Member(BaseObject):
    id: SnowflakeCouple = attr.ib()
    guild: GuildIDWrapper = attr.ib()
    user: UserIDWrapper = attr.ib()
    nick: typing.Optional[str] = attr.ib()
    avatar: typing.Optional[str] = attr.ib()
    # roles: MemberRolesView = attr.ib()
    joined_at: datetime = attr.ib()
    premium_since: typing.Optional[datetime] = attr.ib()
    deaf: bool = attr.ib()
    mute: bool = attr.ib()
    pending: typing.Optional[bool] = attr.ib()
    communication_disabled_until: typing.Optional[int] = attr.ib()


class MemberIDWrapper:
    def __init__(self, id: typing.Optional[SupportsMemberID] = None, *, state: MemberState) -> None:
        self.state = state
        self.id = self.state.to_unique(id) if id is not None else None

        self.guild = SnowflakeWrapper(state=self.client.guilds)
        self.user = SnowflakeWrapper(state=self.client.users)

        if self.id is not None:
            self.guild.id, self.user.id = self.id.high, self.id.low

    def __repr__(self) -> str:
        return f'MemberIDWrapper(id={self.id!r})'

    @property
    def client(self) -> Client:
        return self.state.client

    def unwrap_id(self) -> SnowflakeCouple:
        if self.id is None:
            raise TypeError('unwrap_id() called on empty wrapper')

        return self.id

    async def unwrap(self) -> Member:
        id = self.unwrap_id()

        member = await self.state.get(id)
        if member is None:
            raise UnknownMemberError(id)

        return member


SupportsMemberID = typing.Union[
    SnowflakeCouple,
    typing.Tuple['SupportsGuildID', 'SupportsUserID'],
    Member,
]
