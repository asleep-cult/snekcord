from .basestate import BaseState, SnowflakeMapping, WeakValueSnowflakeMapping
from .. import rest
from ..objects.stageobject import Stage
from ..utils import Snowflake

__all__ = ('StageState',)


class StageState(BaseState):
    __container__ = SnowflakeMapping
    __recycled_container__ = WeakValueSnowflakeMapping
    __stage_class__ = Stage

    def append(self, data):
        stage = self.get(data['id'])
        if stage is not None:
            stage.update(data)
        else:
            stage = self.__stage_class__.unmarshal(data)

        return stage

    async def fetch(self, stage):
        stage_id = Snowflake.try_snowflake(stage)

        data = await rest.get_stage_instance.request(
            session=self.manager.rest,
            fmt=dict(stage_id=stage_id))

        return self.append(data)
