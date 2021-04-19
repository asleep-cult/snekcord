from ..utils.json import JsonField, JsonTemplate
from ..utils.snowflake import Snowflake

BaseTemplate = JsonTemplate(id=JsonField('id', Snowflake, str))
