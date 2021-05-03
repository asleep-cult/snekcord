from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseTemplate
from ..utils.json import JsonArray, JsonField, JsonTemplate
from ..utils.snowflake import Snowflake

if TYPE_CHECKING:
    from ..objects.channel import (
        GuildChannel, TextChannel, VoiceChannel, DMChannel
    )

GuildChannelTemplate: JsonTemplate[GuildChannel] = JsonTemplate(
    name=JsonField('name'),
    guild_id=JsonField('guild_id', Snowflake, str),
    _permission_overwrites=JsonArray('permission_overwrites'),
    position=JsonField('position'),
    nsfw=JsonField('nsfw'),
    category_id=JsonField('parent_id'),
    type=JsonField('type'),
    __extends__=(BaseTemplate,)
)

TextChannelTemplate: JsonTemplate[TextChannel] = JsonTemplate(
    topic=JsonField('topic'),
    slowmode=JsonField('rate_limit_per_user'),
    last_message_id=JsonField('last_message_id'),
    __extends__=(GuildChannelTemplate,)
)

VoiceChannelTemplate: JsonTemplate[VoiceChannel] = JsonTemplate(
    bitrate=JsonField('bitrate'),
    user_limit=JsonField('user_limit'),
    __extends__=(GuildChannelTemplate,)
)

DMChannelTemplate: JsonTemplate[DMChannel] = JsonTemplate(
    last_message_id=JsonField('last_message_id', Snowflake, str),
    type=JsonField('type'),
    _recipients=JsonArray('recipients'),
    __extends__=(BaseTemplate,)
)
