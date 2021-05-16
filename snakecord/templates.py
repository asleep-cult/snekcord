from .utils import JsonArray, JsonField, JsonTemplate, Snowflake


GuildEmojiTemplate = JsonTemplate(
    name=JsonField('name'),
    _roles=JsonArray('roles'),
    _user=JsonField('user'),
    required_colons=JsonField('required_colons'),
    managed=JsonField('managed'),
    animated=JsonField('animated'),
    available=JsonField('available'),
    __extends__=(BaseTemplate,)
)

GuildWidgetSettingsTemplate = JsonTemplate(
    enabled=JsonField('enabled'),
    channel_id=JsonField('channel_id'),
)

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

WelcomeScreenChannelTemplate = JsonTemplate(
    channel_id=JsonField('channel_id', Snowflake, str),
    description=JsonField('description'),
    enoji_id=JsonField('emoji', Snowflake, str),
    emoji_name=JsonField('emoji_name'),
)

WelcomeScreenTemplate = JsonTemplate(
    description=JsonField('description'),
    _welcome_channels=JsonField('welcome_channels'),
)

MessageTemplate = JsonTemplate(
    channel_id=JsonField('channel_id', Snowflake, str),
    guild_id=JsonField('guild_id', Snowflake, str),
    _author=JsonField('author'),
    _member=JsonField('member', default=dict),
    content=JsonField('content'),
    edited_timestamp=JsonField('edited_timestamp'),
    tts=JsonField('tts'),
    mention_everyone=JsonField('mention_everyone'),
    _mentions=JsonArray('mentions'),
    _mention_roles=JsonArray('mention_roles'),
    _mention_channels=JsonArray('mention_channels'),
    _attachments=JsonArray('attachments'),
    _embeds=JsonArray('embeds'),
    _reactions=JsonArray('reactions'),
    nonce=JsonField('nonce'),
    pinned=JsonField('pinned'),
    webhook_id=JsonField('webhook_id'),
    type=JsonField('type'),
    _activity=JsonField('activity'),
    application=JsonField('application'),
    _message_reference=JsonField('message_reference'),
    flags=JsonField('flags'),
    _stickers=JsonArray('stickers'),
    _referenced_message=JsonField('referenced_message'),
    _interaction=JsonField('interaction'),
    __extends__=(BaseTemplate,)
)

ReactionTemplate = JsonTemplate(
    count=JsonField('count'),
    me=JsonField('me'),
    emoji=JsonField('emoji')
)

WebSocketResponseTemplate = JsonTemplate(
    opcode=JsonField('op'),
    sequence=JsonField('s'),
    name=JsonField('t'),
    data=JsonField('d'),
)

WebSocketResponse = WebSocketResponseTemplate.default_object(
    'WebSocketResponse'
)
