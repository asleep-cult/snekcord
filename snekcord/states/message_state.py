import typing

from ..objects import Message, SnowflakeWrapper
from ..snowflake import Snowflake

__all__ = ('SupportsMessageID', 'MessageIDWrapper')

SupportsMessageID = typing.Union[Snowflake, str, int, Message]
MessageIDWrapper = SnowflakeWrapper[SupportsMessageID, Message]
