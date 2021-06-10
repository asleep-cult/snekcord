from __future__ import annotations

import typing as t

from .basestate import BaseState
from .. import rest
from ..objects.stageobject import StageInstance, StageInstancePrivacyLevel
from ..utils import Snowflake, _validate_keys

__all__ = ('StageState',)

if t.TYPE_CHECKING:
    from ..typing import Json, SnowflakeType


class StageState(BaseState[Snowflake, StageInstance]):
    __key_transformer__ = Snowflake.try_snowflake
    __stage_instance_class__ = StageInstance

    def upsert(self, data: Json) -> StageInstance:  # type: ignore
        stage = self.get(data['id'])
        if stage is not None:
            stage.update(data)
        else:
            stage = self.__stage_instance_class__.unmarshal(data, state=self)
            stage.cache()

        return stage

    async def fetch(  # type: ignore
        self, stage: SnowflakeType
    ) -> StageInstance:
        stage_id = Snowflake.try_snowflake(stage)

        data = await rest.get_stage_instance.request(
            session=self.client.rest,
            fmt=dict(stage_id=stage_id))

        return self.upsert(data)

    async def create(self, **kwargs: t.Any) -> StageInstance:
        try:
            kwargs['channel_id'] = Snowflake.try_snowflake(
                kwargs.pop('channel'))
        except KeyError:
            pass

        try:
            kwargs['privacy_level'] = StageInstancePrivacyLevel.get_value(
                kwargs['privacy_level'])
        except KeyError:
            pass

        _validate_keys(f'{self.__class__.__name__}.create',  # type: ignore
                       kwargs, ('channel_id', 'topic'),
                       rest.create_stage_instance.json)

        data = await rest.create_stage_instance.request(
            session=self.client.rest,
            json=kwargs)

        return self.upsert(data)
