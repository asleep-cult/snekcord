import string as _string

# For whatever reason string.Formatter is implemented as a class
# that wraps the '_string' module but doesn't use static methods
_formatter_parse = _string.Formatter().parse

MAJOR_PARAMS = {'channel_id', 'guild_id', 'webhook_id', 'webhook_token'}


class RESTEndpoint:
    __slots__ = ('method', 'path', 'keywords', 'major_params')

    def __init__(self, method, path):
        self.method = method
        self.path = path

        self.keywords = set()
        for text, name, spec, conversion in _formatter_parse(self.path):
            if name is not None:
                self.keywords.add(name)

        self.major_params = self.keywords & MAJOR_PARAMS

    def __repr__(self):
        return f'RESTEndpoint(method={self.method!r}, path={self.path!r})'


GET = 'GET'
PUT = 'PUT'
POST = 'POST'
PATCH = 'PATCH'
DELETE = 'DELETE'

GET_GUILD_AUDIT_LOG = RESTEndpoint(GET, '/guilds/{guild_id}/audit-logs')

GET_CHANNEL = RESTEndpoint(GET, '/channels/{channel_id}')
MODIFY_CHANNEL = RESTEndpoint(PATCH, '/channels/{channel_id}')
DELETE_CHANNEL = RESTEndpoint(DELETE, '/channels/{channel_id}')

TRIGGER_CHANNEL_TYPING = RESTEndpoint(POST, '/channels/{channel_id}/typing')

CREATE_CHANNEL_FOLLOWER = RESTEndpoint(POST, '/channels/{channel_id}/followers')

GET_CHANNEL_PINS = RESTEndpoint(GET, '/channels/{channel_id}/pins')
ADD_CHANNEL_PIN = RESTEndpoint(PUT, '/channels/{channel_id}/pins/{message_id}')
REMOVE_CHANNEL_PIN = RESTEndpoint(DELETE, '/channels/{channel_id}/pins/{message_id}')

ADD_CHANNEL_PERMISSION = RESTEndpoint(POST, '/channels/{channel_id}/permissions/{overwrite_id}')
REMOVE_CHANNEL_PERMISSION = RESTEndpoint(
    DELETE, '/channels/{channel_id}/permissions/{overwrite_id}'
)

GET_CHANNEL_INVITES = RESTEndpoint(GET, '/channels/{channel_id}/invites')
CREATE_CHANNEL_INVITE = RESTEndpoint(POST, '/channels/{channel_id}/invites')

ADD_CHANNEL_RECIPIENT = RESTEndpoint(POST, '/channels/{channel_id}/recipients/{user_id}')
REMOVE_CHANNEL_RECIPIENT = RESTEndpoint(DELETE, '/channels/{channel_id}/recipients/{user_id}')

GET_CHANNEL_MESSAGES = RESTEndpoint(GET, '/channels/{channel_id}/messages')
DELETE_CHANNEL_MESSAGES = RESTEndpoint(DELETE, '/channels/{channel_id}/messages/bulk-delete')
CREATE_CHANNEL_MESSAGE = RESTEndpoint(POST, '/channels/{channel_id}/messages')

GET_CHANNEL_MESSAGE = RESTEndpoint(GET, '/channels/{channel_id}/messages/{message_id}')
MODIFY_CHANNEL_MESSAGE = RESTEndpoint(PATCH, '/channels/{channel_id}/messages/{message_id}')
DELETE_CHANNEL_MESSAGE = RESTEndpoint(DELETE, '/channels/{channel_id}/messages/{message_id}')

CROSSPOST_CHANNEL_MESSAGE = RESTEndpoint(
    POST, '/channels/{channel_id}/messages/{message_id}/crosspost'
)

ADD_MESSAGE_REACTION = RESTEndpoint(
    PUT, '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me'
)
REMOVE_MY_MESSAGE_REACTION = RESTEndpoint(
    DELETE, '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me'
)
REMOVE_MESSAGE_REACTION = RESTEndpoint(
    DELETE, '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}'
)
CLEAR_MESSAGE_REACTIONS = RESTEndpoint(
    DELETE, '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}'
)
CLEAR_ALL_MESSAGE_REACTIONS = RESTEndpoint(
    DELETE, '/channels/{channel_id}/messages/{message_id}/reactions'
)

GET_GUILD_EMOJIS = RESTEndpoint(GET, '/guilds/{guild_id}/emojis')
CREATE_GUILD_EMOJI = RESTEndpoint(POST, '/guilds/{guild_id}/emojis')

GET_GUILD_EMOJI = RESTEndpoint(GET, '/guilds/{guild_id}/emojis/{emoji}')
MODIFY_GUILD_EMOJI = RESTEndpoint(PATCH, '/guilds/{guild_id}/emojis/{emoji}')
DELETE_GUILD_EMOJI = RESTEndpoint(DELETE, '/guilds/{guild_id}/emojis/{emoji}')

CREATE_GUILD = RESTEndpoint(POST, '/guilds')

CREATE_GUILD_FROM_TEMPLATE = RESTEndpoint(POST, '/guilds/templates/{template_code}')

GET_GUILD = RESTEndpoint(GET, '/guilds/{guild_id}')
MODIFY_GUILD = RESTEndpoint(PATCH, '/guilds/{guild_id}')
DELETE_GUILD = RESTEndpoint(DELETE, '/guilds/{guild_id}')

GET_GUILD_PREVIEW = RESTEndpoint(GET, '/guilds/{guild_id}/preview')

GET_GUILD_VOICE_REGIONS = RESTEndpoint(GET, '/guilds/{guild_id}/regions')

GET_GUILD_INVITES = RESTEndpoint(GET, '/guilds/{guild_id}/invites')

GET_GUILD_VANITY_URL = RESTEndpoint(GET, '/guilds/{guild_id}/vanity-url')

GET_GUILD_INTEGRATIONS = RESTEndpoint(GET, '/guilds/{guild_id}/integrations')

DELETE_GUILD_INTEGRATIONS = RESTEndpoint(DELETE, '/guilds/{guild_id}/integrations/{integration_id}')

GET_GUILD_WIDGET = RESTEndpoint(GET, '/guilds/{guild_id}/widget')
MODIFY_GUILD_WIDGET = RESTEndpoint(PATCH, '/guilds/{guild_id}/widget')

GET_GUILD_WIDGET_JSON = RESTEndpoint(GET, '/guilds/{guild_id}/widget.json')
GET_GUILD_WIDGET_IMAGE = RESTEndpoint(GET, '/guilds/{guild_id}/widget.png')

GET_GUILD_WELCOME_SCREEN = RESTEndpoint(GET, '/guilds/{guild_id}/welcome-screen')
MODIFY_GUILD_WELCOME_SCREEN = RESTEndpoint(PATCH, '/guilds/{guild_id}/welcome-screen')

GET_GUILD_PRUNE_COUNT = RESTEndpoint(GET, '/guilds/{guild_id}/prune')
BEGIN_GUILD_PRUNE = RESTEndpoint(POST, '/guilds/{guild_id}/prune')

GET_GUILD_CHANNELS = RESTEndpoint(GET, '/guilds/{guild_id}/channels')
CREATE_GUILD_CHANNEL = RESTEndpoint(POST, '/guilds/{guild_id}/channels')
MODIFY_GUILD_CHANNEL_POSITIONS = RESTEndpoint(PATCH, '/guilds/{guild_id}/channels')

GET_GUILD_MEMBERS = RESTEndpoint(GET, '/guilds/{guild_id}/members')
SEARCH_GUILD_MEMBERS = RESTEndpoint(GET, '/guilds/{guild_id}/members/search')

GET_GUILD_MEMBER = RESTEndpoint(GET, '/guilds/{guild_id}/members/{user_id}')
ADD_GUILD_MEMBER = RESTEndpoint(PUT, '/guilds/{guild_id}/members/{user_id}')
REMOVE_GUILD_MEMBER = RESTEndpoint(DELETE, '/guilds/{guild_id}/members/{user_id}')
MODIFY_GUILD_MEMBER = RESTEndpoint(PATCH, '/guilds/{guild_id}/members/{user_id}')

MODIFY_MY_MEMBER = RESTEndpoint(PATCH, '/guilds/{guild_id}/members/@me')
MODIFY_MY_NICKNAME = RESTEndpoint(PATCH, '/guilds/{guild_id}/members/@me/nick')

ADD_MEMBER_ROLE = RESTEndpoint(PUT, '/guilds/{guild_id}/members/{member_id}/roles/{role_id}')
REMOVE_MEMBER_ROLE = RESTEndpoint(DELETE, '/guilds/{guild_id}/members/{member_id}/roles/{role_id}')

GET_GUILD_BANS = RESTEndpoint(GET, '/guilds/{guild_id}/bans')

GET_GUILD_BAN = RESTEndpoint(GET, '/guilds/{guild_id}/bans/{user_id}')
ADD_GUILD_BAN = RESTEndpoint(PUT, '/guilds/{guild_id}/bans/{user_id}')
REMOVE_GUILD_BAN = RESTEndpoint(DELETE, '/guilds/{guild_id}/bans/{user_id}')

GET_GUILD_ROLES = RESTEndpoint(GET, '/guilds/{guild_id}/roles')
CREATE_GUILD_ROLE = RESTEndpoint(POST, '/guilds/{guild_id}/roles')
MODIFY_GUILD_ROLES = RESTEndpoint(PATCH, '/guilds/{guild_id}/roles')

MODIFY_GUILD_ROLE = RESTEndpoint(PATCH, '/guilds/{guild_id}/roles/{role_id}')
DELETE_GUILD_ROLE = RESTEndpoint(DELETE, '/guilds/{guild_id}/roles/{role_id}')

MODIFY_VOICE_STATE = RESTEndpoint(PATCH, '/guilds/{guild_id}/voice-states/{user_id}')
MODIFY_MY_VOICE_STATE = RESTEndpoint(PATCH, '/guilds/{guild_id}/voice-states/@me')

GET_GUILD_TEMPLATES = RESTEndpoint(GET, '/guilds/{guild_id}/templates')
CREATE_GUILD_TEMPLATE = RESTEndpoint(POST, '/guilds/{guild_id}/templates')

GET_GUILD_TEMPLATE = RESTEndpoint(GET, '/guilds/{guild_id}/templates/{template_code}')
MODIFY_GUILD_TEMPLATE = RESTEndpoint(PATCH, '/guilds/{guild_id}/templates/{template_code}')
DELETE_GUILD_TEMPLATE = RESTEndpoint(DELETE, '/guilds/{guild_id}/templates/{template_code}')

SYNC_GUILD_TEMPLATE = RESTEndpoint(PUT, '/guilds/{guild_id}/templates/{template_code}/sync')

GET_INVITE = RESTEndpoint(GET, '/invites/{invite_code}')
DELETE_INVITE = RESTEndpoint(DELETE, '/invites/{invite_code}')

CREATE_STAGE_INSTANCE = RESTEndpoint(POST, '/stage-instances')

GET_STAGE_INSTANCE = RESTEndpoint(GET, '/stage-instances/{channel_id}')
MODIFY_STAGE_INSTANCE = RESTEndpoint(PATCH, '/stage-instances/{channel_id}')
DELETE_STAGE_INSTANCE = RESTEndpoint(DELETE, '/stage-instances/{channel_id}')

GET_STICKER_PACKS = RESTEndpoint(GET, '/sticker-packs')

GET_STICKER = RESTEndpoint(GET, '/stickers/{sticker_id}')

GET_GUILD_STICKERS = RESTEndpoint(GET, '/guilds/{guild_id}/stickers')

GET_GUILD_STICKER = RESTEndpoint(GET, '/guilds/{guild_id}/stickers/{sticker_id}')
CREATE_GUILD_STICKER = RESTEndpoint(POST, '/guilds/{guild_id}/stickers/{sticker_id}')
MODIFY_GUILD_STICKER = RESTEndpoint(PATCH, '/guilds/{guild_id}/stickers/{sticker_id}')
DELETE_GUILD_STICKER = RESTEndpoint(DELETE, '/guilds/{guild_id}/stickers/{sticker_id}')

GET_USER = RESTEndpoint(GET, '/users/{user_id}')
GET_MY_USER = RESTEndpoint(GET, '/users/@me')
MODIFY_MY_USER = RESTEndpoint(PATCH, '/users/@me')

GET_MY_GUILDS = RESTEndpoint(GET, '/users/@me/guilds')

LEAVE_GUILD = RESTEndpoint(DELETE, 'users/@me/guilds/{guild_id}')

CREATE_DM = RESTEndpoint(POST, '/users/@me/channels')

GET_MY_CONNECTIONS = RESTEndpoint(GET, '/users/@me/connections')

GET_VOICE_REGIONS = RESTEndpoint(GET, '/voice/regions')

GET_GATEWAY = RESTEndpoint(GET, '/gateway')
GET_GATEWAY_BOT = RESTEndpoint(GET, '/gateway/bot')

GET_CHANNEL_WEBHOOKS = RESTEndpoint(GET, '/channels/{channel_id}/webhooks')

GET_GUILD_WEBHOOKS = RESTEndpoint(GET, '/guilds/{guild_id}/webhooks')
