from .baseobject import BaseObject, BaseTemplate
from .. import rest
from ..utils import JsonField, JsonTemplate, Snowflake


StageTemplate = JsonTemplate(
    guild_id=JsonField('guild_id', Snowflake, str),
    channel_id=JsonField('channel_id', Snowflake, str),
    topic=JsonField('topic'),
    __extends__=(BaseTemplate,)
)


class Stage(BaseObject, template=StageTemplate):
    @property
    def guild(self):
        return self.state.manager.guilds.get(self.guild_id)

    @property
    def channel(self):
        return self.state.manager.channels.get(self.channel_id)

    async def modify(self, topic):
        json = {'topic': topic}

        data = await rest.modify_stage_instance.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.channel_id),
            json=json)

        self.update(data)

        return self

    async def delete(self):
        await rest.delete_stage_instance.request(
            session=self.state.manager.rest,
            fmt=dict(channel_id=self.channel_id))
