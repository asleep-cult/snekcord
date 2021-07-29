from .basestate import BaseState
from .. import rest
from ..clients.client import ClientClasses
from ..objects.stageobject import StageInstancePrivacyLevel
from ..utils import Snowflake

__all__ = ('StageInstanceState',)


class StageInstanceState(BaseState):
    def upsert(self, data):
        stage = self.get(Snowflake(data['id']))

        if stage is not None:
            stage.update(data)
        else:
            stage = ClientClasses.StageInstance.unmarshal(data, state=self)
            stage.cache()

        return stage

    async def fetch(self, stage):
        channel_id = Snowflake.try_snowflake(stage)

        data = await rest.get_stage_instance.request(
            self.client.rest, channel_id=channel_id
        )

        return self.upsert(data)

    async def create(self, *, channel, topic, privacy_level=None):
        json = {}

        json['channel_id'] = Snowflake.try_snowflake(channel)

        json['topic'] = str(topic)

        if privacy_level is not None:
            json['privacy_level'] = StageInstancePrivacyLevel.get_value(privacy_level)

        data = await rest.create_stage_instance.request(self.client.rest, json=json)

        return self.upsert(data)

    async def delete(self, stage):
        channel_id = Snowflake.try_snowflake(stage)

        await rest.delete_stage_instance.request(self.client.rest, channel_id=channel_id)
