from __future__ import annotations

import typing as t

from .basestate import BaseState
from ..objects.stageobject import StageInstance
from ..typedefs import SnowflakeConvertible
from ..utils.snowflake import Snowflake

__all__ = ('StageInstanceState',)


class StageInstanceState(
        BaseState[SnowflakeConvertible, Snowflake, StageInstance]):
    async def fetch(self, stage: SnowflakeConvertible) -> StageInstance: ...

    async def create(self, **kwargs: t.Any) -> StageInstance: ...
