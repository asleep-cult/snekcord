from .baseobject import BaseObject
from .. import rest
from ..enums import StageInstancePrivacyLevel
from ..json import JsonField
from ..snowflake import Snowflake

__all__ = ('StageInstance',)


class StageInstance(BaseObject):
    id = JsonField('channel_id', Snowflake)
    raw_id = JsonField('id', Snowflake)
    guild_id = JsonField('guild_id', Snowflake)
    topic = JsonField('topic')
    privacy_level = JsonField('privacy_level', StageInstancePrivacyLevel.get_enum)
    discoverable_disabled = JsonField('discoverable_disabled')

    @property
    def channel_id(self):
        return self.id

    @property
    def guild(self):
        return self.state.client.guilds.get(self.guild_id)

    @property
    def channel(self):
        return self.state.client.channels.get(self.id)

    def fetch(self):
        return self.state.fetch(self.id)

    async def modify(self, *, topic=None, privacy_level=None):
        json = {}

        if topic is not None:
            json['topic'] = str(topic)

        if privacy_level is not None:
            json['privacy_level'] = StageInstancePrivacyLevel.get_value(privacy_level)

        data = await rest.modify_stage_instance.request(
            self.state.client.rest, channel_id=self.id, json=json
        )

        return self.state.upsert(data)

    def delete(self):
        return self.state.delete(self.id)
