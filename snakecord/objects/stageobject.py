from .baseobject import BaseObject, BaseTemplate
from .. import rest
from ..utils import JsonField, JsonTemplate, Snowflake

__all__ = ('Stage',)


StageTemplate = JsonTemplate(
    guild_id=JsonField('guild_id', Snowflake, str),
    channel_id=JsonField('channel_id', Snowflake, str),
    topic=JsonField('topic'),
    __extends__=(BaseTemplate,)
)


class Stage(BaseObject, template=StageTemplate):
    async def modify(self, topic):
        json = {'topic': topic}

        data = await rest.modify_stage_instance.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.channel_id),
            json=json)

        return await self.state.new(data)

    async def delete(self):
        await rest.delete_stage_instance.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.channel_id))
