from .basestate import BaseState
from .. import rest
from ..objects.stageobject import Stage, StagePrivacyLevel
from ..utils import Snowflake, _validate_keys

__all__ = ('StageState',)


class StageState(BaseState):
    __key_transformer__ = Snowflake.try_snowflake
    __stage_class__ = Stage

    def upsert(self, data):
        stage = self.get(data['id'])
        if stage is not None:
            stage.update(data)
        else:
            stage = self.__stage_class__.unmarshal(data, state=self)
            stage.cache()

        return stage

    async def fetch(self, stage):
        stage_id = Snowflake.try_snowflake(stage)

        data = await rest.get_stage_instance.request(
            session=self.manager.rest,
            fmt=dict(stage_id=stage_id))

        return self.upsert(data)

    async def create(self, **kwargs):
        try:
            kwargs['channel_id'] = Snowflake.try_snowflake(
                kwargs.pop('channel'))
        except KeyError:
            pass

        try:
            kwargs['privacy_level'] = StagePrivacyLevel.get_value(
                kwargs['privacy_level'])
        except KeyError:
            pass

        _validate_keys(f'{self.__class__.__name__}.create',
                       kwargs, ('channel_id', 'topic'),
                       rest.create_stage_instance.json)

        data = await rest.create_stage_instance.request(
            session=self.manager.rest,
            json=kwargs)

        return self.upsert(data)
