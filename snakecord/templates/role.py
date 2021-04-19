from .base import BaseTemplate
from ..utils.json import JsonField, JsonTemplate
from ..utils.snowflake import Snowflake

RoleTagTemplate = JsonTemplate(
    bot_id=JsonField('bot_id', Snowflake, str),
    integration_id=JsonField('integration_id', Snowflake, str),
    premium_subscriber=JsonField('premium_subscriber')
)

RoleTemplate = JsonTemplate(
    name=JsonField('name'),
    color=JsonField('color'),
    hoist=JsonField('hoist'),
    position=JsonField('position'),
    permissions=JsonField('permissions'),
    managed=JsonField('managed'),
    mentionable=JsonField('mentionable'),
    tags=JsonField('tags', object=RoleTagTemplate.default_object()),
    __extends__=(BaseTemplate,)
)
