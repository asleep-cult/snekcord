from .basestate import BaseState
from .. import rest
from ..clients.client import ClientClasses
from ..objects.stageobject import StageInstancePrivacyLevel
from ..utils import _validate_keys
from ..utils.snowflake import Snowflake

__all__ = ('StageInstanceState',)


class StageInstanceState(BaseState):
    __key_transformer__ = Snowflake.try_snowflake

    def upsert(self, data):
        stage = self.get(Snowflake(data['id']))

        if stage is not None:
            stage.update(data)
        else:
            stage = ClientClasses.StageInstance.unmarshal(data, state=self)
            stage.cache()

        return stage

    async def fetch(self, stage):
        stage_id = Snowflake.try_snowflake(stage)

        data = await rest.get_stage_instance.request(
            session=self.client.rest,
            fmt=dict(stage_id=stage_id))

        return self.upsert(data)

    async def create(self, **kwargs):
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

        _validate_keys(f'{self.__class__.__name__}.create',
                       kwargs, ('channel_id', 'topic'),
                       rest.create_stage_instance.json)

        data = await rest.create_stage_instance.request(
            session=self.client.rest,
            json=kwargs)

        return self.upsert(data)
