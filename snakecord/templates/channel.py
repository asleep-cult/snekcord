from .base import BaseTemplate
from ..utils.json import JsonArray, JsonField, JsonTemplate
from ..utils.snowflake import Snowflake

GuildChannelTemplate = JsonTemplate(
    name=JsonField('name'),
    guild_id=JsonField('guild_id', Snowflake, str),
    _permission_overwrites=JsonArray('permission_overwrites'),
    position=JsonField('position'),
    nsfw=JsonField('nsfw'),
    parent_id=JsonField('parent_id'),
    type=JsonField('type'),
    __extends__=(BaseTemplate,)
)

TextChannelTemplate = JsonTemplate(
    topic=JsonField('topic'),
    slowmode=JsonField('rate_limit_per_user'),
    last_message_id=JsonField('last_message_id'),
    _extends__=(GuildChannelTemplate,)
)

VoiceChannelTemplate = JsonTemplate(
    bitrate=JsonField('bitrate'),
    user_limit=JsonField('user_limit'),
    __extends__=(GuildChannelTemplate,)
)

DMChannelTemplate = JsonTemplate(
    last_message_id=JsonField('last_message_id', Snowflake, str),
    type=JsonField('type'),
    _recipients=JsonArray('recipients'),
    __extends__=(BaseTemplate,)
)
