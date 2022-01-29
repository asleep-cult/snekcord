import typing

from .base_state import CachedEventState
from ..objects import (
    CachedUser,
    SnowflakeWrapper,
    User,
)
from ..snowflake import Snowflake

__all__ = ('SupportsUserID', 'UserIDWrapper')

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
