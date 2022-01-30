import typing

from .base_state import CachedEventState
from ..enum import convert_enum
from ..objects import (
    CachedUser,
    PremiumType,
    SnowflakeWrapper,
    User,
    UserFlags,
)
from ..snowflake import Snowflake
from ..undefined import undefined

if typing.TYPE_CHECKING:
    from ..json import JSONObject

__all__ = (
    'SupportsUserID',
    'UserIDWrapper',
    'UserState',
)

SupportsUserID = typing.Union[Snowflake, str, int, User]
UserIDWrapper = SnowflakeWrapper[SupportsUserID, User]


class UserState(CachedEventState[SupportsUserID, Snowflake, CachedUser, User]):
    def to_unique(self, object: SupportsUserID) -> Snowflake:
        if isinstance(object, Snowflake):
            return object

        elif isinstance(object, (str, int)):
            return Snowflake(object)

        elif isinstance(object, User):
            return object.id

        raise TypeError('Expectes, Snowflake, str, int, or User')

    async def upsert(self, data: JSONObject) -> User:
        user_id = Snowflake(data['id'])
        data['id'] = user_id

        async with self.synchronize(user_id):
            cached = await self.cache.get(user_id)

            if cached is None:
                cached = CachedUser.from_json(data)
                await self.cache.create(user_id, cached)
            else:
                cached.update(data)
                await self.cache.update(user_id, cached)

        return await self.from_cached(cached)

    async def from_cached(self, cached: CachedUser) -> User:
        flags = undefined.nullify(cached.flags)
        if flags is not None:
            flags = UserFlags(flags)

        premium_type = undefined.nullify(cached.premium_type)
        if premium_type is not None:
            premium_type = convert_enum(PremiumType, premium_type)

        public_flags = undefined.nullify(cached.public_flags)
        if public_flags is not None:
            public_flags = UserFlags(public_flags)

        return User(
            state=self,
            id=Snowflake(cached.id),
            username=cached.username,
            discriminator=cached.discriminator,
            avatar=cached.avatar,
            bot=undefined.nullify(cached.bot),
            system=undefined.nullify(cached.system),
            mfa_enabled=undefined.nullify(cached.mfa_enabled),
            banner=undefined.nullify(cached.banner),
            accent_color=undefined.nullify(cached.accent_color),
            locale=undefined.nullify(cached.locale),
            verified=undefined.nullify(cached.verified),
            email=undefined.nullify(cached.email),
            flags=flags,
            premium_type=premium_type,
            public_flags=public_flags,
        )
