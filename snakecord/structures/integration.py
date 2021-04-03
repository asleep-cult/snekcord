from .base import BaseObject
from ..utils import JsonField, Snowflake, Json


class GuildIntegrationAccount(BaseObject, base=False):
    __json_fields__ = {
        'name': JsonField('name'),
    }

    name: str


class GuildIntegrationApplication(BaseObject, base=False):
    __json_fields__ = {
        'name': JsonField('name'),
        'icon': JsonField('icon'),
        'description': JsonField('description'),
        'summary': JsonField('summary'),
        '_bot': JsonField('bot'),
    }

    name: str
    icon: str
    description: str
    summary: str
    _bot: Json


class GuildIntegration(BaseObject, base=False):
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

    name: str
    type: int
    enabled: bool
    syncing: bool
    role_id: Snowflake
    enable_emoticons: bool
    expire_behavior: int
    expire_grace_period: int  # ?
    _user: Json
    account: GuildIntegrationAccount
    synced_at: str
    subscriber_count: int
    revoked: bool
    _application: Json
