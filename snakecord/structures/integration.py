from .base import BaseObject
from ..utils import JsonField, Snowflake


class GuildIntegrationAccount(BaseObject):
    __json_fields__ = {
        'name': JsonField('name'),
    }


class GuildIntegrationApplication(BaseObject):
    __json_fields__ = {
        'name': JsonField('name'),
        'icon': JsonField('icon'),
        'description': JsonField('description'),
        'summary': JsonField('summary'),
        '_bot': JsonField('bot'),
    }


class GuildIntegration(BaseObject):
    __json_fields__ = {
        'name':  JsonField('name'),
        'type': JsonField('type'),
        'enabled': JsonField('enabled'),
        'syncing': JsonField('syncing'),
        'role_id': JsonField('role_id', Snowflake, str),
        'enable_emoticons': JsonField('enable_emoticons'),
        'expire_behavior': JsonField('expire_behavior'),
        'expire_grace_period': JsonField('expire_grace_period'),
        '_user': JsonField('user'),
        'account': JsonField('account', struct=GuildIntegrationAccount),
        'synced_at': JsonField('synced_at'),
        'subscriber_count': JsonField('subscriber_count'),
        'revoked': JsonField('revoked'),
        '_application': JsonField('application'),
    }
