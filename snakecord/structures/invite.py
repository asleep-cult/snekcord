from ..utils import JsonField, JsonStructure, Json, Snowflake


class Invite(JsonStructure, base=False):
    __json_fields__ = {
        'code': JsonField('code'),
        '_guild': JsonField('guild'),
        '_channel': JsonField('channel'),
        'guild_id': JsonField('guild_id', Snowflake, str),
        'channel_id': JsonField('channel_id', Snowflake, str),
        '_inviter': JsonField('inviter'),
        '_target_user': JsonField('target_user'),
        'target_user_type': JsonField('target_user_type'),
        'approximate_presence_count': JsonField('approximate_presence_count'),
        'approximate_member_count': JsonField('approximate_member_count'),

        # metadata
        'uses': JsonField('uses'),
        'max_uses': JsonField('max_uses'),
        'temporary': JsonField('temporary'),
        'created_at': JsonField('created_at'),
    }

    code: str
    _guild: Json
    _channel: Json
    guild_id: Snowflake
    channel_id: Snowflake
    _inviter: Json
    _target_user: Json
    target_user_type: int
    approximate_presence_count: int
    approximate_member_count: int
    uses: int
    max_uses: int
    temporary: bool
    created_at: str


class PartialInvite(JsonStructure, base=False):
    __json_fields__ = {
        'code': JsonField('code'),
        'uses': JsonField('uses'),
    }

    code: str
    uses: int
