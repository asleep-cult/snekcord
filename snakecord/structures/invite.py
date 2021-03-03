from ..utils import JsonField, JsonStructure


class Invite(JsonStructure):
    __json_fields__ = {
        'code': JsonField('code'),
        '_guild': JsonField('guild'),
        '_channel': JsonField('channel'),
        'guild_id': JsonField('guild_id'),
        'channel_id': JsonField('channel_id'),
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


class PartialInvite(JsonStructure):
    __json_fields__ = {
        'code': JsonField('code'),
        'uses': JsonField('uses'),
    }
