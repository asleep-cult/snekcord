from .baseobject import BaseTemplate
from ..utils import JsonField, JsonTemplate, Snowflake


IntegrationAccountTemplate = JsonTemplate(
    name=JsonField('name'),
    __extends__=(BaseTemplate,)
)

IntegrationAccount = IntegrationAccountTemplate.default_object(
    'IntegrationAccount'
)

IntegrationApplicationTemplate = JsonTemplate(
    name=JsonField('name'),
    icon=JsonField('icon'),
    description=JsonField('description'),
    summary=JsonField('summary'),
    _bot=JsonField('bot'),
    __extends__=(BaseTemplate,)
)

IntegrationTemplate = JsonTemplate(
    name=JsonField('name'),
    type=JsonField('type'),
    enabled=JsonField('enabled'),
    syncing=JsonField('syncing'),
    role_id=JsonField('role_id', Snowflake, str),
    enable_emoticons=JsonField('emoticons'),
    expire_behavior=JsonField('expire_behavior'),
    expire_grace_period=JsonField('expire_grace_period'),
    _user=JsonField('user'),
    account=JsonField('account', object=IntegrationAccount),
    synced_at=JsonField('synced_at'),
    subscriber_count=JsonField('subscriber_count'),
    revoked=JsonField('revoked'),
    _application=JsonField('application'),
    __extends__=(BaseTemplate,)
)
