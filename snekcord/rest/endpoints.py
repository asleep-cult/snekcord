import string

_formatter = string.Formatter()


class HTTPEndpoint:
    def __init__(self, method, url):
        self.method = method
        self.url = url
        self.keywords = [key[1] for key in _formatter.parse(url) if key[1]]

    def request(self, session, *args, **kwargs):
        kwargs['keywords'] = {keyword: kwargs.pop(keyword) for keyword in self.keywords}
        return session.request(self.method, self.url, *args, **kwargs)


BASE_API_URL = 'https://discord.com/api/v9'

get_guild_audit_log = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/audit-logs',
)

get_channel = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/channels/{channel_id}',
)

modify_channel = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/channels/{channel_id}',
)

delete_channel = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/{channel_id}',
)

get_channel_messages = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/channels/{channel_id}/messages',
)

get_channel_message = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/channels/{channel_id}/messages/{message_id}',
)

create_channel_message = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/channels/{channel_id}/messages',
)

crosspost_message = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/channels/{channel_id}/messages/{message_id}/crosspost',
)

add_reaction = HTTPEndpoint(
    'PUT',
    BASE_API_URL + '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me',
)

remove_reaction = HTTPEndpoint(
    'DELETE',
    BASE_API_URL
    + '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}'
)

get_reactions = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/channels/{channel_id}/messages/{message_id}/reactions/{emoji_id}',
)

remove_reactions = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}',
)

remove_all_reactions = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/{channel_id}/messages/{message_id}/reactions',
)

modify_message = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/channels/{channel_id}/messages/{message_id}',
)

delete_message = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/{channel_id}/messages/{message_id}',
)

bulk_delete_messages = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/channels/{channel_id}/messages/bulk-delete',
)

create_channel_permission_overwrite = HTTPEndpoint(
    'PUT',
    BASE_API_URL + '/channels/{channel_id}/permissions/{overwrite_id}',
)

delete_channel_permission_overwrite = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/{channel_id}/permissions/{overwrite_id}',
)

get_channel_invites = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/channels/{channel_id}/invites',
)

create_channel_invite = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/channels/{channel_id}/invites',
)

add_news_channel_follower = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/channels/{channel_id}/followers',
)

trigger_typing_indicator = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/channels/{channel_id}/typing',
)

get_pinned_messages = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/channels/{channel_id}/pins',
)

add_pinned_message = HTTPEndpoint(
    'PUT',
    BASE_API_URL + '/channels/{channel_id}/pins/{message_id}',
)

remove_pinned_message = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/{channel_id}/pins/{message_id}',
)

add_group_dm_recipient = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/channels/{channel_id}/recipients/{user_id}',
)

delete_group_dm_recipient = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/{channel_id}/recipients/{user_id}',
)

get_guild_emojis = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/emojis',
)

get_guild_emoji = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/emojis/{emoji}',
)

get_emoji_guild = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/emojis/{emoji_id}/guild'
)

create_guild_emoji = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds/{guild_id}/emojis',
)

modify_guild_emoji = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/emojis/{emoji_id}',
)

delete_guild_emoji = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}/emojis/{emoji_id}',
)

get_sticker = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/stickers/{sticker_id}'
)

get_sticker_packs = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/sticker-packs'
)

get_guild_stickers = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/stickers'
)

get_guild_sticker = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/stickers/{sticker_id}'
)

get_sticker_guild = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/stickers/{sticker_id}/guild'
)

create_guild_sticker = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds/{guild_id}/stickers'
)

modify_guild_sticker = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/stickers/{sticker_id}'
)

delete_guild_sticker = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}/stickers/{sticker_id}'
)

create_guild = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds',
)

get_guild = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}',
)

get_guild_preview = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/preview',
)

modify_guild = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}',
)

delete_guild = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}',
)

get_guild_channels = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/channels',
)

create_guild_channel = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds/{guild_id}/channels',
)

modify_guild_channels = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/channels',
)

get_guild_member = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/members/{user_id}',
)

get_guild_members = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/members',
)

search_guild_members = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/members/search',
)

add_guild_member = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds/{guild_id}/members/{user_id}',
)

modify_guild_member = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/members/{user_id}',
)

modify_self_nick = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/members/@me/nick',
)

add_guild_member_role = HTTPEndpoint(
    'PUT',
    BASE_API_URL + '/guilds/{guild_id}/members/{user_id}/roles/{role_id}',
)

remove_guild_member_role = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}/members/{user_id}/roles/{role_id}',
)

remove_guild_member = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}/members/{user_id}',
)

get_guild_bans = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/bans',
)

get_guild_ban = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/bans/{user_id}'
)

create_guild_ban = HTTPEndpoint(
    'PUT',
    BASE_API_URL + '/guilds/{guild_id}/bans/{user_id}',
)

remove_guild_ban = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}/bans/{user_id}',
)

get_guild_roles = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/roles',
)

create_guild_role = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds/{guild_id}/roles',
)

modify_guild_roles = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/roles',
)

modify_guild_role = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/roles/{role_id}',
)

delete_guild_role = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}/roles/{role_id}',
)

get_guild_prune_count = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/prune',
)

begin_guild_prune = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds/{guild_id}/prune',
)

get_guild_voice_regions = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/regions',
)

get_guild_invites = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/invites',
)

get_guild_integrations = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/integrations',
)

delete_guild_integration = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}/integrations/{integration_id}'
)

get_guild_widget_settings = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/widget',
)

modify_guild_widget_settings = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/widget',
)

get_guild_widget = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/widget.json',
)

get_guild_vanity_url = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/vanity-url',
)

get_guild_welcome_screen = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/welcome-screen',
)

modify_guild_welcome_screen = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/welcome-screen',
)

modify_self_voice_state = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/voice-states/@me',
)

modify_user_voice_state = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/voice-states/{user_id}',
)

get_invite = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/invites/{invite_code}',
)

delete_invite = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/invites/{invite_code}',
)

create_stage_instance = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/stage-instances',
)

get_stage_instance = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/stage-instances/{channel_id}',
)

modify_stage_instance = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/stage-instances/{channel_id}',
)

delete_stage_instance = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/stage-instances/{channel_id}',
)

get_template = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/templates/{template_code}',
)

create_guild_from_template = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds/templates/{template_code}',
)

get_guild_templates = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/templates'
)

create_guild_template = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds/{guild_id}/templates',
)

sync_guild_template = HTTPEndpoint(
    'PUT',
    BASE_API_URL + '/guilds/{guild_id}/templates/{template_code}',
)

modify_guild_template = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/templates/{template_code}',
)

delete_guild_template = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}/templates/{template_code}',
)

get_me = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/users/@me',
)

get_user = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/users/{user_id}'
)

modify_self = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/users/@me',
)

get_my_guilds = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/users/@me/guilds',
)

leave_guild = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/users/@me/guilds/{guild_id}',
)

create_dm = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/users/@me/channels',
)

create_group_dm = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/users/@me/channels',
)

get_user_connections = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/users/@me/connections'
)

get_voice_regions = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/voice/regions',
)

create_webhook = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/channels/{channel_id}/webhooks',
)

get_channel_webhooks = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/channels/{channel_id}/webhooks',
)

get_guild_webhooks = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/webhooks',
)

get_webhook = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/webhooks/{webhook_id}'
)

get_webhook_with_token = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}',
)

modify_webhook = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/webhooks/{webhook_id}',
)

modify_webhook_with_token = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}',
)

delete_webhook = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/webhooks/{webhook_id}',
)

delete_webhook_with_token = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}',
)

execute_webhook = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}',
)

execute_slack_webhook = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}/slack',
)

execute_github_webhook = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}/github',
)

get_webhook_message = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}'
)

modify_webhook_message = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}',
)

delete_webhook_message = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}',
)

get_gateway = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/gateway'
)

get_gateway_bot = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/gateway/bot'
)
