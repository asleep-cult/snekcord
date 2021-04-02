from ..utils import JsonField, JsonStructure, Snowflake


class VoiceState(JsonStructure, base=True):
    __json_fields__ = {
        'guild_id': JsonField('guild_id', Snowflake, str),
        'channel_id': JsonField('channel_id', Snowflake, str),
        'user_id': JsonField('user_id', Snowflake, str),
        '_member': JsonField('member'),
        'session_id': JsonField('session_id'),
        'deaf': JsonField('deaf'),
        'mute': JsonField('mute'),
        'self_deaf': JsonField('self_deaf'),
        'self_mute': JsonField('self_mute'),
        'self_stream': JsonField('self_stream'),
        'self_video': JsonField('self_video'),
        'suppress': JsonField('suppress'),
    }


class VoiceServerUpdate(JsonStructure, base=True):
    __json_fields__ = {
        'token': JsonField('token'),
        'guild_id': JsonField('guild_id', Snowflake, str),
        'endpoint': JsonField('endpoint'),
    }
