import typing

from .base_state import CachedEventState
from ..objects import (
    CachedMessage,
    Message,
    SnowflakeWrapper,
)
from ..snowflake import Snowflake

__all__ = (
    'SupportsMessageID',
    'MessageIDWrapper',
    'MessageState',
)

SupportsMessageID = typing.Union[Snowflake, str, int, Message]
MessageIDWrapper = SnowflakeWrapper[SupportsMessageID, Message]


class MessageState(CachedEventState[SupportsMessageID, Snowflake, CachedMessage, Message]):
    def to_unique(self, object: SupportsMessageID) -> Snowflake:
        if isinstance(object, Snowflake):
            return object

        elif isinstance(object, (str, int)):
            return Snowflake(object)

        elif isinstance(object, Message):
            return object.id

        raise TypeError('Expected Snowflake, str, int, or Message')
