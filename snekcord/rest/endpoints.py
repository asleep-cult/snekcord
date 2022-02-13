from __future__ import annotations

import enum
import string
import typing

_formatter_parse = string.Formatter().parse

MAJOR_PARAMS = {'channel_id', 'guild_id', 'webhook_id', 'webhook_token'}


class APIEndpoint:
    __slots__ = ('method', 'path', 'keywords', 'major_params')

    def __init__(self, method: str, path: str) -> None:
        self.method = method
        self.path = path

        self.keywords: typing.Set[str] = set()
        for _, name, _, _ in _formatter_parse(self.path):
            if name is not None:
                self.keywords.add(name)

        self.major_params = self.keywords & MAJOR_PARAMS

    def __repr__(self):
        return f'APIEndpoint(method={self.method!r}, path={self.path!r})'

    def url(self, base: str, **kwargs: typing.Any) -> str:
        keywords = {keyword: kwargs.pop(keyword) for keyword in self.keywords}
        return base + self.path.format_map(keywords)


class CDNEndpoint:
    def __init__(self, path: str, formats: typing.Tuple[CDNFormat, ...]) -> None:
        self.path = path
        self.formats = formats

        self.keywords: typing.Set[str] = set()
        for _, name, _, _ in _formatter_parse(self.path):
            if name is not None:
                self.keywords.add(name)

    def __repr__(self) -> str:
        return f'CDNEndpoint(path={self.path!r}, formats={self.formats!r})'

    def url(self, base: str, **kwargs: typing.Any) -> str:
        keywords = {keyword: kwargs.pop(keyword) for keyword in self.keywords}

        format = kwargs.pop('format', CDNFormat.PNG)
        if format not in self.formats:
            raise ValueError(f'Invalid format: {format!r}')

        size = keywords.pop('size', None)
        if size is not None:
            if not 16 <= size <= 4096:
                raise ValueError(f'Size should be >= 16 and <= 4096, got {size!r}')

            if size & (size - 1) != 0:
                raise ValueError(f'Size should be a power of two, got {size!r}')

        url = base + self.path.format_map(keywords) + f'.{format.value}'

        if size is not None:
            url += f'?size={size}'

        return url


class CDNFormat(str, enum.Enum):
    JPEG = 'jpeg'
    PNG = 'png'
    WEBP = 'webp'
    GIF = 'gif'
    LOTTIE = 'lottie'


GET = 'GET'
PUT = 'PUT'
POST = 'POST'
PATCH = 'PATCH'
DELETE = 'DELETE'

GET_GUILD_AUDIT_LOG = APIEndpoint(GET, '/guilds/{guild_id}/audit-logs')

GET_CHANNEL = APIEndpoint(GET, '/channels/{channel_id}')
UPDATE_CHANNEL = APIEndpoint(PATCH, '/channels/{channel_id}')
DELETE_CHANNEL = APIEndpoint(DELETE, '/channels/{channel_id}')

TRIGGER_CHANNEL_TYPING = APIEndpoint(POST, '/channels/{channel_id}/typing')

CREATE_CHANNEL_FOLLOWER = APIEndpoint(POST, '/channels/{channel_id}/followers')

GET_CHANNEL_PINS = APIEndpoint(GET, '/channels/{channel_id}/pins')
ADD_CHANNEL_PIN = APIEndpoint(PUT, '/channels/{channel_id}/pins/{message_id}')
REMOVE_CHANNEL_PIN = APIEndpoint(DELETE, '/channels/{channel_id}/pins/{message_id}')

ADD_CHANNEL_PERMISSION = APIEndpoint(POST, '/channels/{channel_id}/permissions/{overwrite_id}')
REMOVE_CHANNEL_PERMISSION = APIEndpoint(DELETE, '/channels/{channel_id}/permissions/{overwrite_id}')

GET_CHANNEL_INVITES = APIEndpoint(GET, '/channels/{channel_id}/invites')
CREATE_CHANNEL_INVITE = APIEndpoint(POST, '/channels/{channel_id}/invites')

ADD_CHANNEL_RECIPIENT = APIEndpoint(POST, '/channels/{channel_id}/recipients/{user_id}')
REMOVE_CHANNEL_RECIPIENT = APIEndpoint(DELETE, '/channels/{channel_id}/recipients/{user_id}')

GET_CHANNEL_MESSAGES = APIEndpoint(GET, '/channels/{channel_id}/messages')
DELETE_CHANNEL_MESSAGES = APIEndpoint(POST, '/channels/{channel_id}/messages/bulk-delete')
CREATE_CHANNEL_MESSAGE = APIEndpoint(POST, '/channels/{channel_id}/messages')

GET_CHANNEL_MESSAGE = APIEndpoint(GET, '/channels/{channel_id}/messages/{message_id}')
UPDATE_CHANNEL_MESSAGE = APIEndpoint(PATCH, '/channels/{channel_id}/messages/{message_id}')
DELETE_CHANNEL_MESSAGE = APIEndpoint(DELETE, '/channels/{channel_id}/messages/{message_id}')

CROSSPOST_CHANNEL_MESSAGE = APIEndpoint(
    POST, '/channels/{channel_id}/messages/{message_id}/crosspost'
)

ADD_MESSAGE_REACTION = APIEndpoint(
    PUT, '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me'
)
REMOVE_MY_MESSAGE_REACTION = APIEndpoint(
    DELETE, '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me'
)
REMOVE_MESSAGE_REACTION = APIEndpoint(
    DELETE, '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}'
)
CLEAR_MESSAGE_REACTIONS = APIEndpoint(
    DELETE, '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}'
)
CLEAR_ALL_MESSAGE_REACTIONS = APIEndpoint(
    DELETE, '/channels/{channel_id}/messages/{message_id}/reactions'
)

GET_GUILD_EMOJIS = APIEndpoint(GET, '/guilds/{guild_id}/emojis')
CREATE_GUILD_EMOJI = APIEndpoint(POST, '/guilds/{guild_id}/emojis')

GET_GUILD_EMOJI = APIEndpoint(GET, '/guilds/{guild_id}/emojis/{emoji}')
UPDATE_GUILD_EMOJI = APIEndpoint(PATCH, '/guilds/{guild_id}/emojis/{emoji}')
DELETE_GUILD_EMOJI = APIEndpoint(DELETE, '/guilds/{guild_id}/emojis/{emoji}')

CREATE_GUILD = APIEndpoint(POST, '/guilds')

CREATE_GUILD_FROM_TEMPLATE = APIEndpoint(POST, '/guilds/templates/{template_code}')

GET_GUILD = APIEndpoint(GET, '/guilds/{guild_id}')
UPDATE_GUILD = APIEndpoint(PATCH, '/guilds/{guild_id}')
DELETE_GUILD = APIEndpoint(DELETE, '/guilds/{guild_id}')

GET_GUILD_PREVIEW = APIEndpoint(GET, '/guilds/{guild_id}/preview')

GET_GUILD_VOICE_REGIONS = APIEndpoint(GET, '/guilds/{guild_id}/regions')

GET_GUILD_INVITES = APIEndpoint(GET, '/guilds/{guild_id}/invites')

GET_GUILD_VANITY_URL = APIEndpoint(GET, '/guilds/{guild_id}/vanity-url')

GET_GUILD_INTEGRATIONS = APIEndpoint(GET, '/guilds/{guild_id}/integrations')

DELETE_GUILD_INTEGRATIONS = APIEndpoint(DELETE, '/guilds/{guild_id}/integrations/{integration_id}')

GET_GUILD_WIDGET = APIEndpoint(GET, '/guilds/{guild_id}/widget')
UPDATE_GUILD_WIDGET = APIEndpoint(PATCH, '/guilds/{guild_id}/widget')

GET_GUILD_WIDGET_JSON = APIEndpoint(GET, '/guilds/{guild_id}/widget.json')
GET_GUILD_WIDGET_IMAGE = APIEndpoint(GET, '/guilds/{guild_id}/widget.png')

GET_GUILD_WELCOME_SCREEN = APIEndpoint(GET, '/guilds/{guild_id}/welcome-screen')
UPDATE_GUILD_WELCOME_SCREEN = APIEndpoint(PATCH, '/guilds/{guild_id}/welcome-screen')

GET_GUILD_PRUNE_COUNT = APIEndpoint(GET, '/guilds/{guild_id}/prune')
BEGIN_GUILD_PRUNE = APIEndpoint(POST, '/guilds/{guild_id}/prune')

GET_GUILD_CHANNELS = APIEndpoint(GET, '/guilds/{guild_id}/channels')
CREATE_GUILD_CHANNEL = APIEndpoint(POST, '/guilds/{guild_id}/channels')
UPDATE_GUILD_CHANNEL_POSITIONS = APIEndpoint(PATCH, '/guilds/{guild_id}/channels')

GET_GUILD_MEMBERS = APIEndpoint(GET, '/guilds/{guild_id}/members')
SEARCH_GUILD_MEMBERS = APIEndpoint(GET, '/guilds/{guild_id}/members/search')

GET_GUILD_MEMBER = APIEndpoint(GET, '/guilds/{guild_id}/members/{user_id}')
ADD_GUILD_MEMBER = APIEndpoint(PUT, '/guilds/{guild_id}/members/{user_id}')
REMOVE_GUILD_MEMBER = APIEndpoint(DELETE, '/guilds/{guild_id}/members/{user_id}')
UPDATE_GUILD_MEMBER = APIEndpoint(PATCH, '/guilds/{guild_id}/members/{user_id}')

UPDATE_MY_MEMBER = APIEndpoint(PATCH, '/guilds/{guild_id}/members/@me')
UPDATE_MY_NICKNAME = APIEndpoint(PATCH, '/guilds/{guild_id}/members/@me/nick')

ADD_MEMBER_ROLE = APIEndpoint(PUT, '/guilds/{guild_id}/members/{member_id}/roles/{role_id}')
REMOVE_MEMBER_ROLE = APIEndpoint(DELETE, '/guilds/{guild_id}/members/{member_id}/roles/{role_id}')

GET_GUILD_BANS = APIEndpoint(GET, '/guilds/{guild_id}/bans')

GET_GUILD_BAN = APIEndpoint(GET, '/guilds/{guild_id}/bans/{user_id}')
ADD_GUILD_BAN = APIEndpoint(PUT, '/guilds/{guild_id}/bans/{user_id}')
REMOVE_GUILD_BAN = APIEndpoint(DELETE, '/guilds/{guild_id}/bans/{user_id}')

GET_GUILD_ROLES = APIEndpoint(GET, '/guilds/{guild_id}/roles')
CREATE_GUILD_ROLE = APIEndpoint(POST, '/guilds/{guild_id}/roles')
UPDATE_GUILD_ROLE_POSITIONS = APIEndpoint(PATCH, '/guilds/{guild_id}/roles')

UPDATE_GUILD_ROLE = APIEndpoint(PATCH, '/guilds/{guild_id}/roles/{role_id}')
DELETE_GUILD_ROLE = APIEndpoint(DELETE, '/guilds/{guild_id}/roles/{role_id}')

UPDATE_VOICE_STATE = APIEndpoint(PATCH, '/guilds/{guild_id}/voice-states/{user_id}')
UPDATE_MY_VOICE_STATE = APIEndpoint(PATCH, '/guilds/{guild_id}/voice-states/@me')

GET_GUILD_TEMPLATES = APIEndpoint(GET, '/guilds/{guild_id}/templates')
CREATE_GUILD_TEMPLATE = APIEndpoint(POST, '/guilds/{guild_id}/templates')

GET_GUILD_TEMPLATE = APIEndpoint(GET, '/guilds/{guild_id}/templates/{template_code}')
UPDATE_GUILD_TEMPLATE = APIEndpoint(PATCH, '/guilds/{guild_id}/templates/{template_code}')
DELETE_GUILD_TEMPLATE = APIEndpoint(DELETE, '/guilds/{guild_id}/templates/{template_code}')

SYNC_GUILD_TEMPLATE = APIEndpoint(PUT, '/guilds/{guild_id}/templates/{template_code}/sync')

GET_INVITE = APIEndpoint(GET, '/invites/{invite_code}')
DELETE_INVITE = APIEndpoint(DELETE, '/invites/{invite_code}')

CREATE_STAGE_INSTANCE = APIEndpoint(POST, '/stage-instances')

GET_STAGE_INSTANCE = APIEndpoint(GET, '/stage-instances/{channel_id}')
UPDATE_STAGE_INSTANCE = APIEndpoint(PATCH, '/stage-instances/{channel_id}')
DELETE_STAGE_INSTANCE = APIEndpoint(DELETE, '/stage-instances/{channel_id}')

GET_STICKER_PACKS = APIEndpoint(GET, '/sticker-packs')

GET_STICKER = APIEndpoint(GET, '/stickers/{sticker_id}')

GET_GUILD_STICKERS = APIEndpoint(GET, '/guilds/{guild_id}/stickers')

GET_GUILD_STICKER = APIEndpoint(GET, '/guilds/{guild_id}/stickers/{sticker_id}')
CREATE_GUILD_STICKER = APIEndpoint(POST, '/guilds/{guild_id}/stickers/{sticker_id}')
UPDATE_GUILD_STICKER = APIEndpoint(PATCH, '/guilds/{guild_id}/stickers/{sticker_id}')
DELETE_GUILD_STICKER = APIEndpoint(DELETE, '/guilds/{guild_id}/stickers/{sticker_id}')

GET_USER = APIEndpoint(GET, '/users/{user_id}')
GET_MY_USER = APIEndpoint(GET, '/users/@me')
UPDATE_MY_USER = APIEndpoint(PATCH, '/users/@me')

GET_MY_GUILDS = APIEndpoint(GET, '/users/@me/guilds')

LEAVE_GUILD = APIEndpoint(DELETE, 'users/@me/guilds/{guild_id}')

CREATE_DM = APIEndpoint(POST, '/users/@me/channels')

GET_MY_CONNECTIONS = APIEndpoint(GET, '/users/@me/connections')

GET_VOICE_REGIONS = APIEndpoint(GET, '/voice/regions')

GET_GATEWAY = APIEndpoint(GET, '/gateway')
GET_GATEWAY_BOT = APIEndpoint(GET, '/gateway/bot')

GET_CHANNEL_WEBHOOKS = APIEndpoint(GET, '/channels/{channel_id}/webhooks')

GET_GUILD_WEBHOOKS = APIEndpoint(GET, '/guilds/{guild_id}/webhooks')

CUSTOM_EMOJI = CDNEndpoint(
    '/emojis/{emoji_id}', (CDNFormat.PNG, CDNFormat.JPEG, CDNFormat.WEBP, CDNFormat.GIF)
)
GUILD_ICON = CDNEndpoint(
    '/icons/{guild_id}/{guild_icon}', (CDNFormat.PNG, CDNFormat.JPEG, CDNFormat.WEBP, CDNFormat.GIF)
)
GUILD_SPLASH = CDNEndpoint(
    '/splashed/{guild_id}/{guild_splash}', (CDNFormat.PNG, CDNFormat.JPEG, CDNFormat.WEBP)
)
GUILD_DISCOVERY_SPLASH = CDNEndpoint(
    '/discovery-splashes/{guild_id}/{guild_discovery_splash}',
    (CDNFormat.PNG, CDNFormat.JPEG, CDNFormat.WEBP),
)
GUILD_BANNER = CDNEndpoint(
    '/banners/{guild_id}/{guild_banner}', (CDNFormat.PNG, CDNFormat.JPEG, CDNFormat.WEBP)
)
USER_BANNER = CDNEndpoint(
    '/banners/{user_id}/{user_banner}',
    (CDNFormat.PNG, CDNFormat.JPEG, CDNFormat.WEBP, CDNFormat.GIF),
)
DEFAULT_USER_AVATAR = CDNEndpoint('/embed/avatars/{user_discriminator}', (CDNFormat.PNG,))
USER_AVATAR = CDNEndpoint(
    '/avatars/{user_id}/{user_avatar}',
    (CDNFormat.PNG, CDNFormat.JPEG, CDNFormat.WEBP, CDNFormat.GIF),
)
GUILD_MEMBER_AVATAR = CDNEndpoint(
    '/guilds/{guild_id}/users/{user_id}/avatars/{member_avatar}',
    (CDNFormat.PNG, CDNFormat.JPEG, CDNFormat.WEBP, CDNFormat.GIF),
)
APPLICATION_ICON = CDNEndpoint(
    '/app-icons/{application_id}/{icon}', (CDNFormat.PNG, CDNFormat.JPEG, CDNFormat.WEBP)
)
APPLICATION_COVER = CDNEndpoint(
    '/app-icons/{application_id}/{cover_image}', (CDNFormat.PNG, CDNFormat.JPEG, CDNFormat.WEBP)
)
APPLICATION_ASSET = CDNEndpoint(
    '/app-assets/{application_id}/{asset_id}', (CDNFormat.PNG, CDNFormat.JPEG, CDNFormat.WEBP)
)
ACHIEVEMENT_ICON = CDNEndpoint(
    '/app-assets/{application_id}/achievements/{achievement_id}/icons/{icon}',
    (CDNFormat.PNG, CDNFormat.JPEG, CDNFormat.WEBP),
)
STICKER_PACK_BANNER = CDNEndpoint(
    'app-assets/710982414301790216/store/{sticker_pack_banner_asset_id}',
    (CDNFormat.PNG, CDNFormat.JPEG, CDNFormat.WEBP),
)
TEAM_ICON = CDNEndpoint(
    'team-icons/{team_id}/{team_icon}', (CDNFormat.PNG, CDNFormat.JPEG, CDNFormat.WEBP)
)
STICKER = CDNEndpoint('stickers/{sticker_id}', (CDNFormat.PNG, CDNFormat.LOTTIE))
GUILD_SCHEDULED_EVENT_COVER = CDNEndpoint(
    'guild-events/{scheduled_event_id}/{scheduled_event_cover_image}',
    (CDNFormat.PNG, CDNFormat.JPEG, CDNFormat.WEBP),
)
