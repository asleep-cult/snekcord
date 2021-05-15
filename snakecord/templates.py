from .utils import JsonArray, JsonField, JsonTemplate, Snowflake

__all__ = ('BaseTemplate', 'GuildChannelTemplate', 'TextChannelTemplate',
           'VoiceChannelTemplate', 'DMChannelTemplate', 'GuildEmojiTemplate',
           'GuildPreviewTemplate', 'GuildTemplate', 'GuildBanTemplate',
           'GuildWidgetSettingsTemplate', 'GuildWidgetChannelTemplate',
           'GuildWidgetMemberTemplate', 'GuildWidgetTemplate',
           'GuildMemberTemplate', 'IntegrationAccountTemplate',
           'IntegrationApplicationTemplate', 'IntegrationTemplate',
           'WelcomeScreenChannelTemplate', 'WelcomeScreenTemplate',
           'MessageTemplate', 'ReactionTemplate', 'RoleTagsTemplate',
           'RoleTemplate', 'UserTemplate')


BaseTemplate = JsonTemplate(
    id=JsonField('id', Snowflake, str),
)

GuildChannelTemplate = JsonTemplate(
    name=JsonField('name'),
    guild_id=JsonField('guild_id', Snowflake, str),
    _permission_overwrites=JsonArray('permission_overwrites'),
    position=JsonField('position'),
    nsfw=JsonField('nsfw'),
    category_id=JsonField('parent_id'),
    type=JsonField('type'),
    __extends__=(BaseTemplate,)
)

TextChannelTemplate = JsonTemplate(
    topic=JsonField('topic'),
    slowmode=JsonField('rate_limit_per_user'),
    last_message_id=JsonField('last_message_id'),
    __extends__=(GuildChannelTemplate,)
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

GuildPreviewTemplate = JsonTemplate(
    name=JsonField('name'),
    icon=JsonField('icon'),
    splash=JsonField('splash'),
    discovery_splash=JsonField('discovery_splash'),
    _emojis=JsonArray('emojis'),
    features=JsonArray('features'),
    member_count=JsonField('approximate_member_count'),
    presence_count=JsonField('approximate_presence_count'),
    description=JsonField('description'),
    __extends__=(BaseTemplate,)
)

GuildTemplate = JsonTemplate(
    icon_hash=JsonField('icon_hash'),
    owner=JsonField('owner'),
    owner_id=JsonField('owner_id', Snowflake, str),
    permissions=JsonField('permissions'),
    region=JsonField('region'),
    afk_channel_id=JsonField('afk_channel_id', Snowflake, str),
    afk_timeout=JsonField('afk_timeout'),
    widget_enabled=JsonField('widget_enabled'),
    widget_channel_id=JsonField('widget_channel_id', Snowflake, str),
    verification_level=JsonField('verification_level'),
    default_message_notifications=JsonField('default_message_notifications'),
    explicit_content_filter=JsonField('explicit_content_filter'),
    _roles=JsonArray('roles'),
    mfa_level=JsonField('mfa_level'),
    application_id=JsonField('application_id', Snowflake, str),
    system_channel_id=JsonField('system_channel_id', Snowflake, str),
    system_channel_flags=JsonField('system_channel_flags'),
    rules_channel_id=JsonField('rules_channel_id', Snowflake, str),
    joined_at=JsonField('joined_at'),
    large=JsonField('large'),
    unavailable=JsonField('unavailable'),
    member_count=JsonField('member_count'),
    _voice_states=JsonArray('voice_states'),
    _members=JsonArray('members'),
    _channels=JsonArray('channels'),
    _threads=JsonArray('threads'),
    _presences=JsonArray('presences'),
    max_presences=JsonField('max_presences'),
    max_members=JsonField('max_members'),
    vanity_url_code=JsonField('vanity_url_code'),
    banner=JsonField('banner'),
    premium_tier=JsonField('permium_tier'),
    premium_subscription_count=JsonField('premium_subscription_count'),
    preferred_locale=JsonField('preferred_locale'),
    public_updates_channel_id=JsonField(
        'public_updates_channel_id', Snowflake, str
    ),
    max_video_channel_users=JsonField('max_video_channel_users'),
    welcome_screen=JsonField('welcome_screen'),
    nsfw=JsonField('nsfw'),
    __extends__=(GuildPreviewTemplate,)
)

GuildBanTemplate = JsonTemplate(
    reason=JsonField('reason'),
    _user=JsonField('user')
)

GuildWidgetSettingsTemplate = JsonTemplate(
    enabled=JsonField('enabled'),
    channel_id=JsonField('channel_id'),
)

GuildWidgetChannelTemplate = JsonTemplate(
    name=JsonField('name'),
    position=JsonField('position'),
    __extends__=(BaseTemplate,)
)

GuildWidgetMemberTemplate = JsonTemplate(
    username=JsonField('username'),
    discriminator=JsonField('discriminator'),
    avatar=JsonField('avatar'),
    status=JsonField('status'),
    avatar_url=JsonField('avatar_url'),
    __extends__=(BaseTemplate,)
)

GuildWidgetTemplate = JsonTemplate(
    name=JsonField('name'),
    instant_invite=JsonField('instant_invite'),
    _channels=JsonArray('channels'),
    _members=JsonArray('members'),
    presence_count=JsonField('presence_count'),
    __extends__=(BaseTemplate,)
)

GuildMemberTemplate = JsonTemplate(
    _user=JsonField('user'),
    nick=JsonField('nick'),
    _roles=JsonArray('roles'),
    joined_at=JsonField('joined_at'),
    premium_since=JsonField('premium_since'),
    deaf=JsonField('deaf'),
    mute=JsonField('mute'),
    pending=JsonField('pending'),
    _permissions=JsonField('permissions'),
)

IntegrationAccountTemplate = JsonTemplate(
    name=JsonField('name'),
    __extends__=(BaseTemplate,)
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
    account=JsonField(
        'account',
        object=IntegrationAccountTemplate.default_object(
            'IntegrationAccount'
        )
    ),
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

WelcomeScreenTemplate = JsonField(
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

RoleTagsTemplate = JsonTemplate(
    bot_id=JsonField('bot_id', Snowflake, str),
    integration_id=JsonField('integration_id', Snowflake, str),
    premium_subscriber=JsonField('premium_subscriber')
)

RoleTemplate = JsonTemplate(
    name=JsonField('name'),
    color=JsonField('color'),
    hoist=JsonField('hoist'),
    position=JsonField('position'),
    permissions=JsonField('permissions'),
    managed=JsonField('managed'),
    mentionable=JsonField('mentionable'),
    tags=JsonField(
        'tags',
        object=RoleTagsTemplate.default_object('RoleTags')
    ),
    __extends__=(BaseTemplate,)
)

InviteTemplate = JsonTemplate(
    code=JsonField('code'),
    _guild=JsonField('guild'),
    _channel=JsonField('channel'),
    _inviter=JsonField('inviter'),
    terget_type=JsonField('target_type'),
    _target_user=JsonField('target_user'),
    _target_application=JsonField('target_application'),
    presence_count=JsonField('approximate_presence_count'),
    member_count=JsonField('approximate_member_count'),
    expires_at=JsonField('expires_at'),

    uses=JsonField('uses'),
    max_uses=JsonField('max_uses'),
    max_age=JsonField('max_age'),
    temporary=JsonField('temporary'),
    created_at=JsonField('temporary'),
)

UserTemplate = JsonTemplate(
    name=JsonField('username'),
    discriminator=JsonField('discriminator'),
    avatar=JsonField('avatar'),
    bot=JsonField('bot'),
    system=JsonField('system'),
    mfa_enabled=JsonField('mfa_enabled'),
    locale=JsonField('locale'),
    verified=JsonField('verified'),
    email=JsonField('email'),
    flags=JsonField('flags'),
    premium_type=JsonField('premium_type'),
    public_flags=JsonField('public_flags'),
    __extends__=(BaseTemplate,)
)

WebSocketResponse = JsonTemplate(
    opcode=JsonField('op'),
    sequence=JsonField('s'),
    name=JsonField('t'),
    data=JsonField('d'),
).default_object()
