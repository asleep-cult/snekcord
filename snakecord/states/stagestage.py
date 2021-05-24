from .basestate import BaseState
from .. import rest
from ..objects.stageobject import Stage
from ..utils import Snowflake

__all__ = ('StageState',)


class StageState(BaseState):
    __key_transformer__ = Snowflake.try_snowflake
    __stage_class__ = Stage

    async def new(self, data):
        stage = await self.get(data['id'])
        if stage is not None:
            await stage.update(data)
        else:
            stage = await self.__stage_class__.unmarshal(data, state=self)
            await stage.cache()

        return stage

    async def fetch(self, stage):
        stage_id = Snowflake.try_snowflake(stage)

        data = await rest.get_stage_instance.request(
            session=self.manager.rest,
            fmt=dict(stage_id=stage_id))

        return await self.new(data)
