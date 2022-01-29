import typing

from ..objects import SnowflakeWrapper, User
from ..snowflake import Snowflake

__all__ = ('SupportsUserID', 'UserIDWrapper')

SupportsUserID = typing.Union[Snowflake, str, int, User]
UserIDWrapper = SnowflakeWrapper[SupportsUserID, User]
