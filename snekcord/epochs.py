from __future__ import annotations

import enum
from datetime import datetime

from .snowflake import Snowflake


class EpochType(enum.IntEnum):
    BEFORE = enum.auto()
    AFTER = enum.auto()
    AROUND = enum.auto()


class BaseEpoch:
    __slots__ = ('type', 'snowflake')

    def __init__(self, *, type: EpochType, snowflake: Snowflake) -> None:
        self.type = type
        self.snowflake = snowflake

    @property
    def key(self) -> str:
        if self.type is EpochType.BEFORE:
            return 'before'
        elif self.type is EpochType.AFTER:
            return 'after'
        elif self.type is EpochType.AROUND:
            return 'around'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(type={self.type!r}, snowflake={self.snowflake})'


class MessageEpoch(BaseEpoch):
    __slots__ = ()

    @classmethod
    def before(cls, message) -> MessageEpoch:
        from .states import MessageState

        if isinstance(message, datetime):
            snowflake = Snowflake.build(timestamp=message.timestamp())
        else:
            snowflake = MessageState.unwrap_id(message)

        return cls(EpochType.BEFORE, snowflake=snowflake)

    @classmethod
    def after(cls, message) -> MessageEpoch:
        from .states import MessageState

        if isinstance(message, datetime):
            snowflake = Snowflake.build(timestamp=message.timestamp())
        else:
            snowflake = MessageState.unwrap_id(message)

        return cls(EpochType.AFTER, snowflake=snowflake)

    @classmethod
    def around(cls, message) -> MessageEpoch:
        from .states import MessageState

        if isinstance(message, datetime):
            snowflake = Snowflake.build(timestamp=message.timestamp())
        else:
            snowflake = MessageState.unwrap_id(message)

        return cls(EpochType.AROUND, snowflake=snowflake)
