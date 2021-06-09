from __future__ import annotations

import typing as t

from .baseobject import BaseObject, BaseTemplate
from .. import rest
from ..utils import (Enum, JsonField, JsonTemplate, Snowflake,
                     _validate_keys)

__all__ = ('StagePrivacyLevel', 'Stage',)

if t.TYPE_CHECKING:
    from ..objects import Guild, GuildChannel
    from ..states import StageState


class StagePrivacyLevel(Enum[int]):
    PUBLIC = 1
    GUILD_ONLY = 2


StageTemplate = JsonTemplate(
    guild_id=JsonField('guild_id', Snowflake, str),
    channel_id=JsonField('channel_id', Snowflake, str),
    topic=JsonField('topic'),
    privacy_level=JsonField(
        'privacy_level',
        StagePrivacyLevel.get_enum,
        StagePrivacyLevel.get_value
    ),
    discoverable_disabled=JsonField('discoverable_disabled'),
    __extends__=(BaseTemplate,)
)


class Stage(BaseObject, template=StageTemplate):
    if t.TYPE_CHECKING:
        state: StageState
        guild_id: Snowflake
        channel_id: Snowflake
        topic: str
        privacy_level: StagePrivacyLevel
        discoverable_disabled: bool

    @property
    def guild(self) -> t.Optional[Guild]:
        return self.state.client.guilds.get(self.guild_id)

    @property
    def channel(self) -> t.Optional[GuildChannel]:
        guild = self.guild
        if guild is not None:
            return guild.channels.get(self.channel_id)

    async def fetch(self) -> Stage:
        return await self.state.fetch(self.channel_id)

    async def modify(self, **kwargs: t.Any):
        try:
            kwargs['privacy_level'] = StagePrivacyLevel.get_value(
                kwargs['privacy_level'])
        except KeyError:
            pass

        _validate_keys(f'{self.__class__.__name__}.modify',  # type: ignore
                       kwargs, (), rest.modify_stage_instance.json)

        data = await rest.modify_stage_instance.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.channel_id),
            json=kwargs)

        return self.state.upsert(data)

    async def delete(self):
        await rest.delete_stage_instance.request(
            session=self.state.client.rest,
            fmt=dict(channel_id=self.channel_id))
