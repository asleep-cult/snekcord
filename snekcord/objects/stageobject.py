from .baseobject import BaseObject
from .. import rest
from ..enums import StageInstancePrivacyLevel
from ..utils import _validate_keys
from ..utils.json import JsonField
from ..utils.snowflake import Snowflake

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

    async def fetch(self):
        return await self.state.fetch(self.channel_id)

    async def modify(self, **kwargs):
        try:
            kwargs['privacy_level'] = StageInstancePrivacyLevel.get_value(kwargs['privacy_level'])
        except KeyError:
            pass

        _validate_keys(f'{self.__class__.__name__}.modify',
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
