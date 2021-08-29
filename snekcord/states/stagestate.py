from .basestate import BaseState
from .. import http
from ..objects.stageobject import StageInstance, StageInstancePrivacyLevel
from ..snowflake import Snowflake

__all__ = ('StageInstanceState',)


class StageInstanceState(BaseState):
    def upsert(self, data):
        stage = self.get(Snowflake(data['channel_id']))

        if stage is not None:
            stage.update(data)
        else:
            stage = StageInstance.unmarshal(data, state=self)
            stage.cache()

        return stage

    async def fetch(self, stage):
        channel_id = Snowflake.try_snowflake(stage)

        data = await http.get_stage_instance.request(
            self.client.http, channel_id=channel_id
        )

        return self.upsert(data)

    async def create(self, *, channel, topic, privacy_level=None):
        json = {}

        json['channel_id'] = Snowflake.try_snowflake(channel)

        json['topic'] = str(topic)

        if privacy_level is not None:
            json['privacy_level'] = StageInstancePrivacyLevel.try_value(privacy_level)

        data = await http.create_stage_instance.request(self.client.http, json=json)

        return self.upsert(data)

    async def delete(self, stage):
        channel_id = Snowflake.try_snowflake(stage)

        await http.delete_stage_instance.request(self.client.http, channel_id=channel_id)
