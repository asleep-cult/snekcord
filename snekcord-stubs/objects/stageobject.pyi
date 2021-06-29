from __future__ import annotations

import typing as t

from .baseobject import BaseObject
from .channelobject import GuildChannel
from .guildobject import Guild
from ..states.stagestate import StageInstanceState
from ..utils.enum import Enum
from ..utils.json import JsonTemplate
from ..utils.snowflake import Snowflake


class StageInstancePrivacyLevel(Enum[int]):
    PUBLIC = 1
    GUILD_ONLY = 2


StageInstanceTemplate: JsonTemplate = ...


class StageInstance(BaseObject[Snowflake], template=StageInstanceTemplate):
    guild_id: Snowflake
    channel_id: Snowflake
    topic: str
    privacy_level: StageInstanceTemplate
    discoverable_disabled: bool

    state: StageInstanceState

    def __init__(self, *, state: StageInstanceState) -> None: ...

    @property
    def guild(self) -> Guild | None: ...

    @property
    def channel(self) -> GuildChannel: ...

    async def fetch(self) -> StageInstance: ...

    async def modify(self, **kwargs: t.Any) -> StageInstance: ...

    async def delete(self) -> None: ...
