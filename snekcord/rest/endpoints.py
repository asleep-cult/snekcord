import string

_formatter = string.Formatter()


class RestEndpoint:
    def __init__(self, method, url):
        self.method = method
        self.url = url
        self.keywords = [key[1] for key in _formatter.parse(url) if key[1]]

    def request(self, session, *args, **kwargs):
        kwargs['keywords'] = {keyword: kwargs.pop(keyword) for keyword in self.keywords}
        return session.request(self.method, self.url, *args, **kwargs)


BASE_API_URL = 'https://discord.com/api/v9'
BASE_CDN_URL = 'https://cdn.discordapp.com'

get_guild_audit_log = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/audit-logs',
)

get_channel = RestEndpoint(
    'GET',
    BASE_API_URL + '/channels/{channel_id}',
)

modify_channel = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/channels/{channel_id}',
)

delete_channel = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/{channel_id}',
)

get_channel_messages = RestEndpoint(
    'GET',
    BASE_API_URL + '/channels/{channel_id}/messages',
)

get_channel_message = RestEndpoint(
    'GET',
    BASE_API_URL + '/channels/{channel_id}/messages/{message_id}',
)

create_channel_message = RestEndpoint(
    'POST',
    BASE_API_URL + '/channels/{channel_id}/messages',
)

crosspost_message = RestEndpoint(
    'POST',
    BASE_API_URL + '/channels/{channel_id}/messages/{message_id}/crosspost',
)

add_reaction = RestEndpoint(
    'PUT',
    BASE_API_URL + '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me',
)

remove_reaction = RestEndpoint(
    'DELETE',
    BASE_API_URL
    + '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}'
)

get_reactions = RestEndpoint(
    'GET',
    BASE_API_URL + '/channels/{channel_id}/messages/{message_id}/reactions/{emoji_id}',
)

remove_reactions = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/{channel_id}/messages/{message_id}/reactions/{emoji}',
)

remove_all_reactions = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/{channel_id}/messages/{message_id}/reactions',
)

modify_message = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/channels/{channel_id}/messages/{message_id}',
)

delete_message = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/{channel_id}/messages/{message_id}',
)

bulk_delete_messages = RestEndpoint(
    'POST',
    BASE_API_URL + '/channels/{channel_id}/messages/bulk-delete',
)

create_channel_permission_overwrite = RestEndpoint(
    'PUT',
    BASE_API_URL + '/channels/{channel_id}/permissions/{overwrite_id}',
)

delete_channel_permission_overwrite = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/{channel_id}/permissions/{overwrite_id}',
)

get_channel_invites = RestEndpoint(
    'GET',
    BASE_API_URL + '/channels/{channel_id}/invites',
)

create_channel_invite = RestEndpoint(
    'POST',
    BASE_API_URL + '/channels/{channel_id}/invites',
)

add_news_channel_follower = RestEndpoint(
    'POST',
    BASE_API_URL + '/channels/{channel_id}/followers',
)

trigger_typing_indicator = RestEndpoint(
    'POST',
    BASE_API_URL + '/channels/{channel_id}/typing',
)

get_pinned_messages = RestEndpoint(
    'GET',
    BASE_API_URL + '/channels/{channel_id}/pins',
)

add_pinned_message = RestEndpoint(
    'PUT',
    BASE_API_URL + '/channels/{channel_id}/pins/{message_id}',
)

remove_pinned_message = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/{channel_id}/pins/{message_id}',
)

add_group_dm_recipient = RestEndpoint(
    'POST',
    BASE_API_URL + '/channels/{channel_id}/recipients/{user_id}',
)

delete_group_dm_recipient = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/{channel_id}/recipients/{user_id}',
)

get_guild_emojis = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/emojis',
)

get_guild_emoji = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/emojis/{emoji}',
)

get_emoji_guild = RestEndpoint(
    'GET',
    BASE_API_URL + '/emojis/{emoji_id}/guild'
)

create_guild_emoji = RestEndpoint(
    'POST',
    BASE_API_URL + '/guilds/{guild_id}/emojis',
)

modify_guild_emoji = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/emojis/{emoji_id}',
)

delete_guild_emoji = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}/emojis/{emoji_id}',
)

get_sticker = RestEndpoint(
    'GET',
    BASE_API_URL + '/stickers/{sticker_id}'
)

get_sticker_packs = RestEndpoint(
    'GET',
    BASE_API_URL + '/sticker-packs'
)

get_guild_stickers = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/stickers'
)

get_guild_sticker = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/stickers/{sticker_id}'
)

get_sticker_guild = RestEndpoint(
    'GET',
    BASE_API_URL + '/stickers/{sticker_id}/guild'
)

create_guild_sticker = RestEndpoint(
    'POST',
    BASE_API_URL + '/guilds/{guild_id}/stickers'
)

modify_guild_sticker = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/stickers/{sticker_id}'
)

delete_guild_sticker = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}/stickers/{sticker_id}'
)

create_guild = RestEndpoint(
    'POST',
    BASE_API_URL + '/guilds',
)

get_guild = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}',
)

get_guild_preview = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/preview',
)

modify_guild = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}',
)

delete_guild = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}',
)

get_guild_channels = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/channels',
)

create_guild_channel = RestEndpoint(
    'POST',
    BASE_API_URL + '/guilds/{guild_id}/channels',
)

modify_guild_channels = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/channels',
)

get_guild_member = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/members/{user_id}',
)

get_guild_members = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/members',
)

search_guild_members = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/members/search',
)

add_guild_member = RestEndpoint(
    'POST',
    BASE_API_URL + '/guilds/{guild_id}/members/{user_id}',
)

modify_guild_member = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/members/{user_id}',
)

modify_self_nick = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/members/@me/nick',
)

add_guild_member_role = RestEndpoint(
    'PUT',
    BASE_API_URL + '/guilds/{guild_id}/members/{user_id}/roles/{role_id}',
)

remove_guild_member_role = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}/members/{user_id}/roles/{role_id}',
)

remove_guild_member = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}/members/{user_id}',
)

get_guild_bans = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/bans',
)

get_guild_ban = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/bans/{user_id}'
)

create_guild_ban = RestEndpoint(
    'PUT',
    BASE_API_URL + '/guilds/{guild_id}/bans/{user_id}',
)

remove_guild_ban = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}/bans/{user_id}',
)

get_guild_roles = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/roles',
)

create_guild_role = RestEndpoint(
    'POST',
    BASE_API_URL + '/guilds/{guild_id}/roles',
)

modify_guild_roles = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/roles',
)

modify_guild_role = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/roles/{role_id}',
)

delete_guild_role = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}/roles/{role_id}',
)

get_guild_prune_count = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/prune',
)

begin_guild_prune = RestEndpoint(
    'POST',
    BASE_API_URL + '/guilds/{guild_id}/prune',
)

get_guild_voice_regions = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/regions',
)

get_guild_invites = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/invites',
)

get_guild_integrations = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/integrations',
)

delete_guild_integration = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}/integrations/{integration_id}'
)

get_guild_widget_settings = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/widget',
)

modify_guild_widget_settings = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/widget',
)

get_guild_widget = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/widget.json',
)

get_guild_vanity_url = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/vanity-url',
)

get_guild_welcome_screen = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/welcome-screen',
)

modify_guild_welcome_screen = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/welcome-screen',
)

modify_self_voice_state = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/voice-states/@me',
)

modify_user_voice_state = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/voice-states/{user_id}',
)

get_invite = RestEndpoint(
    'GET',
    BASE_API_URL + '/invites/{invite_code}',
)

delete_invite = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/invites/{invite_code}',
)

create_stage_instance = RestEndpoint(
    'POST',
    BASE_API_URL + '/stage-instances',
)

get_stage_instance = RestEndpoint(
    'GET',
    BASE_API_URL + '/stage-instances/{channel_id}',
)

modify_stage_instance = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/stage-instances/{channel_id}',
)

delete_stage_instance = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/stage-instances/{channel_id}',
)

get_template = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/templates/{template_code}',
)

create_guild_from_template = RestEndpoint(
    'POST',
    BASE_API_URL + '/guilds/templates/{template_code}',
)

get_guild_templates = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/templates'
)

create_guild_template = RestEndpoint(
    'POST',
    BASE_API_URL + '/guilds/{guild_id}/templates',
)

sync_guild_template = RestEndpoint(
    'PUT',
    BASE_API_URL + '/guilds/{guild_id}/templates/{template_code}',
)

modify_guild_template = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/{guild_id}/templates/{template_code}',
)

delete_guild_template = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/{guild_id}/templates/{template_code}',
)

get_me = RestEndpoint(
    'GET',
    BASE_API_URL + '/users/@me',
)

get_user = RestEndpoint(
    'GET',
    BASE_API_URL + '/users/{user_id}'
)

modify_self = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/users/@me',
)

get_my_guilds = RestEndpoint(
    'GET',
    BASE_API_URL + '/users/@me/guilds',
)

leave_guild = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/users/@me/guilds/{guild_id}',
)

create_dm = RestEndpoint(
    'POST',
    BASE_API_URL + '/users/@me/channels',
)

create_group_dm = RestEndpoint(
    'POST',
    BASE_API_URL + '/users/@me/channels',
)

get_user_connections = RestEndpoint(
    'GET',
    BASE_API_URL + '/users/@me/connections'
)

get_voice_regions = RestEndpoint(
    'GET',
    BASE_API_URL + '/voice/regions',
)

create_webhook = RestEndpoint(
    'POST',
    BASE_API_URL + '/channels/{channel_id}/webhooks',
)

get_channel_webhooks = RestEndpoint(
    'GET',
    BASE_API_URL + '/channels/{channel_id}/webhooks',
)

get_guild_webhooks = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/webhooks',
)

get_webhook = RestEndpoint(
    'GET',
    BASE_API_URL + '/webhooks/{webhook_id}'
)

get_webhook_with_token = RestEndpoint(
    'GET',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}',
)

modify_webhook = RestEndpoint(
    'GET',
    BASE_API_URL + '/webhooks/{webhook_id}',
)

modify_webhook_with_token = RestEndpoint(
    'GET',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}',
)

delete_webhook = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/webhooks/{webhook_id}',
)

delete_webhook_with_token = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}',
)

execute_webhook = RestEndpoint(
    'POST',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}',
)

execute_slack_webhook = RestEndpoint(
    'POST',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}/slack',
)

execute_github_webhook = RestEndpoint(
    'POST',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}/github',
)

get_webhook_message = RestEndpoint(
    'GET',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}'
)

modify_webhook_message = RestEndpoint(
    'PATCH',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}',
)

delete_webhook_message = RestEndpoint(
    'DELETE',
    BASE_API_URL + '/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}',
)

get_gateway = RestEndpoint(
    'GET',
    BASE_API_URL + '/gateway'
)

get_gateway_bot = RestEndpoint(
    'GET',
    BASE_API_URL + '/gateway/bot'
)

get_guild_icon = RestEndpoint(
    'GET',
    BASE_CDN_URL + '/icons/{guild_id}/{guild_icon}.{format}'
)

get_guild_splash = RestEndpoint(
    'GET',
    BASE_CDN_URL + '/splashes/{guild_id}/{guild_splash}.{format}'
)

get_guild_discovery_splash = RestEndpoint(
    'GET',
    BASE_CDN_URL + '/discovery-splashes/{guild_id}/{guild_discovery_splash}.{format}'
)

get_guild_banner = RestEndpoint(
    'GET',
    BASE_CDN_URL + '/banners/{guild_id}/{guild_banner}.{format}'
)

get_default_user_avatar = RestEndpoint(
    'GET',
    BASE_CDN_URL + '/embed/avatars/{user_discriminator}.{format}'
)

get_user_avatar = RestEndpoint(
    'GET',
    BASE_CDN_URL + '/avatars/{user_id}/{user_avatar}.{format}'
)

get_application_icon = RestEndpoint(
    'GET',
    BASE_CDN_URL + '/app-icons/{application_id}/{application_icon}.{format}'
)

get_application_cover = RestEndpoint(
    'GET',
    BASE_CDN_URL + '/app-icons/{application_id}/{application_cover_image}.{format}'
)

get_application_asset = RestEndpoint(
    'GET',
    BASE_CDN_URL + '/app-icons/{application_id}/{application_asset}.{format}'
)

get_achievement_icon = RestEndpoint(
    'GET',
    BASE_CDN_URL
    + '/app-icons/{application_id}/achievements/{achievement_id}/icons/{achievement_icon}.{format}'
)

get_team_icon = RestEndpoint(
    'GET',
    BASE_CDN_URL + '/team-icons/{team_id}/{team_icon}.{format}'
)

get_guild_widget_image = RestEndpoint(
    'GET',
    BASE_API_URL + '/guilds/{guild_id}/widget.{format}'
)
