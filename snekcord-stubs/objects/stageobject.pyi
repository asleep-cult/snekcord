from __future__ import annotations

import typing as t

from .baseobject import BaseObject
from .channelobject import GuildChannel
from .guildobject import Guild
from ..enums import StageInstancePrivacyLevel
from ..states.stagestate import StageInstanceState
from ..utils.json import JsonField
from ..utils.snowflake import Snowflake


class StageInstance(BaseObject[Snowflake]):
    guild_id: t.ClassVar[JsonField[Snowflake]]
    channel_id: t.ClassVar[JsonField[Snowflake]]
    topic: t.ClassVar[JsonField[str]]
    privacy_level: t.ClassVar[JsonField[StageInstancePrivacyLevel]]
    discoverable_disabled: t.ClassVar[JsonField[bool]]

    state: StageInstanceState

    def __init__(self, *, state: StageInstanceState) -> None: ...

    @property
    def guild(self) -> Guild | None: ...

    @property
    def channel(self) -> GuildChannel: ...

    async def fetch(self) -> StageInstance: ...

    async def modify(self, **kwargs: t.Any) -> StageInstance: ...

    async def delete(self) -> None: ...
