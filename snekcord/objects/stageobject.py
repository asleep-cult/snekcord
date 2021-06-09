from .baseobject import BaseObject, BaseTemplate
from .. import rest
from ..utils import (Enum, JsonField, JsonTemplate, Snowflake,
                     _validate_keys)

__all__ = ('StageInstancePrivacyLevel', 'StageInstance',)


class StageInstancePrivacyLevel(Enum, type=int):
    PUBLIC = 1
    GUILD_ONLY = 2


StageInstanceTemplate = JsonTemplate(
    guild_id=JsonField('guild_id', Snowflake, str),
    channel_id=JsonField('channel_id', Snowflake, str),
    topic=JsonField('topic'),
    privacy_level=JsonField(
        'privacy_level',
        StageInstancePrivacyLevel.get_enum,
        StageInstancePrivacyLevel.get_value
    ),
    discoverable_disabled=JsonField('discoverable_disabled'),
    __extends__=(BaseTemplate,)
)


class StageInstance(BaseObject, template=StageInstanceTemplate):
    @property
    def guild(self):
        return self.state.manager.guilds.get(self.guild_id)

    @property
    def channel(self):
        return self.state.manager.channels.get(self.channel_id)

    async def fetch(self):
        return await self.state.fetch(self.channel_id)

    async def modify(self, **kwargs):
        try:
            kwargs['privacy_level'] = StageInstancePrivacyLevel.get_value(
                kwargs['privacy_level'])
        except KeyError:
            pass

        _validate_keys(f'{self.__class__.__name__}.modify',
                       kwargs, (), rest.modify_stage_instance.keys)

        data = await rest.modify_stage_instance.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.channel_id),
            json=kwargs)

        return self.state.upsert(data)

    async def delete(self):
        await rest.delete_stage_instance.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.channel_id))
