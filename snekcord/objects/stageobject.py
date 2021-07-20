from .baseobject import BaseObject
from .. import rest
from ..enums import StageInstancePrivacyLevel
from ..utils import JsonField, Snowflake

__all__ = ('StageInstance',)


class StageInstance(BaseObject):
    guild_id = JsonField('guild_id', Snowflake)
    channel_id = JsonField('channel_id', Snowflake)
    topic = JsonField('topic')
    privacy_level = JsonField('privacy_level', StageInstancePrivacyLevel.get_enum)
    discoverable_disabled = JsonField('discoverable_disabled')

    @property
    def guild(self):
        return self.state.client.guilds.get(self.guild_id)

    @property
    def channel(self):
        return self.state.client.channels.get(self.channel_id)

    def fetch(self):
        return self.state.fetch(self.channel_id)

    async def modify(self, *, topic=None, privacy_level=None):
        json = {}

        if topic is not None:
            json['topic'] = str(topic)

        if privacy_level is not None:
            json['privacy_level'] = StageInstancePrivacyLevel.get_value(privacy_level)

        data = await rest.modify_stage_instance.request(
            self.state.client.rest, {'channel_id': self.channel_id}, json=json
        )

        return self.state.upsert(data)

    def delete(self):
        return self.state.delete(self.channel_id)
