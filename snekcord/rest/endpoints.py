class HTTPEndpoint:
    def __init__(self, method, url):
        self.method = method
        self.url = url

    def request(self, session, *args, **kwargs):
        return session.request(self.method, self.url, *args, **kwargs)


BASE_API_URL = 'https://discord.com/api/v9'

get_guild_audit_log = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/audit-logs',
)

get_channel = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/channels/%(channel_id)s',
)

modify_channel = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/channels/%(channel_id)s',
)

delete_channel = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/%(channel_id)s',
)

get_channel_messages = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/channels/%(channel_id)s/messages',
)

get_channel_message = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/channels/%(channel_id)s/messages/%(message_id)s',
)

create_channel_message = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/channels/%(channel_id)s/messages',
)

crosspost_message = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/channels/%(channel_id)s/messages/%(message_id)s/crosspost',
)

add_reaction = HTTPEndpoint(
    'PUT',
    BASE_API_URL + '/channels/%(channel_id)s/messages/%(message_id)s/reactions/%(emoji)s/@me',
)

remove_reaction = HTTPEndpoint(
    'DELETE',
    BASE_API_URL
    + '/channels/%(channel_id)s/messages/%(message_id)s/reactions/%(emoji)s/%(user_id)s'
)

get_reactions = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/channels/%(channel_id)s/messages/%(message_id)s/reactions/%(emoji_id)s',
)

remove_reactions = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/%(channel_id)s/messages/%(message_id)s/reactions/%(emoji)s',
)

remove_all_reactions = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/%(channel_id)s/messages/%(message_id)s/reactions',
)

modify_message = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/channels/%(channel_id)s/messages/%(message_id)s',
)

delete_message = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/%(channel_id)s/messages/%(message_id)s',
)

bulk_delete_messages = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/channels/%(channel_id)s/messages/bulk-delete',
)

create_channel_permission_overwrite = HTTPEndpoint(
    'PUT',
    BASE_API_URL + '/channels/%(channel_id)s/permissions/%(overwrite_id)s',
)

delete_channel_permission_overwrite = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/%(channel_id)s/permissions/%(overwrite_id)s',
)

get_channel_invites = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/channels/%(channel_id)s/invites',
)

create_channel_invite = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/channels/%(channel_id)s/invites',
)

add_news_channel_follower = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/channels/%(channel_id)s/followers',
)

trigger_typing_indicator = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/channels/%(channel_id)s/typing',
)

get_pinned_messages = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/channels/%(channel_id)s/pins',
)

add_pinned_message = HTTPEndpoint(
    'PUT',
    BASE_API_URL + '/channels/%(channel_id)s/pins/%(message_id)s',
)

remove_pinned_message = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/%(channel_id)s/pins/%(message_id)s',
)

add_group_dm_recipient = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/channels/%(channel_id)s/recipients/%(user_id)s',
)

delete_group_dm_recipient = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/channels/%(channel_id)s/recipients/%(user_id)s',
)

get_guild_emojis = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/emojis',
)

get_guild_emoji = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/emojis/%(emoji)s',
)

get_emoji_guild = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/emojis/%(emoji_id)s/guild'
)

create_guild_emoji = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds/%(guild_id)s/emojis',
)

modify_guild_emoji = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/%(guild_id)s/emojis/%(emoji_id)s',
)

delete_guild_emoji = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/%(guild_id)s/emojis/%(emoji_id)s',
)

get_sticker = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/stickers/%(sticker_id)s'
)

get_sticker_packs = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/sticker-packs'
)

get_guild_stickers = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/stickers'
)

get_guild_sticker = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/stickers/%(sticker_id)s'
)

get_sticker_guild = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/stickers/%(sticker_id)s/guild'
)

create_guild_sticker = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds/%(guild_id)s/stickers'
)

modify_guild_sticker = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/%(guild_id)s/stickers/%(sticker_id)s'
)

delete_guild_sticker = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/%(guild_id)s/stickers/%(sticker_id)s'
)

create_guild = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds',
)

get_guild = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s',
)

get_guild_preview = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/preview',
)

modify_guild = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/%(guild_id)s',
)

delete_guild = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/%(guild_id)s',
)

get_guild_channels = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/channels',
)

create_guild_channel = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds/%(guild_id)s/channels',
)

modify_guild_channels = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/%(guild_id)s/channels',
)

get_guild_member = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/members/%(user_id)s',
)

get_guild_members = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/members',
)

search_guild_members = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/members/search',
)

add_guild_member = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds/%(guild_id)s/members/%(user_id)s',
)

modify_guild_member = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/%(guild_id)s/members/%(user_id)s',
)

modify_self_nick = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/%(guild_id)s/members/@me/nick',
)

add_guild_member_role = HTTPEndpoint(
    'PUT',
    BASE_API_URL + '/guilds/%(guild_id)s/members/%(user_id)s/roles/%(role_id)s',
)

remove_guild_member_role = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/%(guild_id)s/members/%(user_id)s/roles/%(role_id)s',
)

remove_guild_member = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/%(guild_id)s/members/%(user_id)s',
)

get_guild_bans = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/bans',
)

get_guild_ban = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/bans/%(user_id)s'
)

create_guild_ban = HTTPEndpoint(
    'PUT',
    BASE_API_URL + '/guilds/%(guild_id)s/bans/%(user_id)s',
)

remove_guild_ban = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/%(guild_id)s/bans/%(user_id)s',
)

get_guild_roles = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/roles',
)

create_guild_role = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds/%(guild_id)s/roles',
)

modify_guild_roles = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/%(guild_id)s/roles',
)

modify_guild_role = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/%(guild_id)s/roles/%(role_id)s',
)

delete_guild_role = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/%(guild_id)s/roles/%(role_id)s',
)

get_guild_prune_count = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/prune',
)

begin_guild_prune = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds/%(guild_id)s/prune',
)

get_guild_voice_regions = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/regions',
)

get_guild_invites = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/invites',
)

get_guild_integrations = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/integrations',
)

delete_guild_integration = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/%(guild_id)s/integrations/%(integration_id)s'
)

get_guild_widget_settings = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/widget',
)

modify_guild_widget_settings = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/%(guild_id)s/widget',
)

get_guild_widget = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/widget.json',
)

get_guild_vanity_url = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/vanity-url',
)

get_guild_welcome_screen = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/welcome-screen',
)

modify_guild_welcome_screen = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/%(guild_id)s/welcome-screen',
)

modify_self_voice_state = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/%(guild_id)s/voice-states/@me',
)

modify_user_voice_state = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/%(guild_id)s/voice-states/%(user_id)s',
)

get_invite = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/invites/%(invite_code)s',
)

delete_invite = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/invites/%(invite_code)s',
)

create_stage_instance = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/stage-instances',
)

get_stage_instance = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/stage-instances/%(channel_id)s',
)

modify_stage_instance = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/stage-instances/%(channel_id)s',
)

delete_stage_instance = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/stage-instances/%(channel_id)s',
)

get_template = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/templates/%(template_code)s',
)

create_guild_from_template = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds/templates/%(template_code)s',
)

get_guild_templates = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/guilds/%(guild_id)s/templates'
)

create_guild_template = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/guilds/%(guild_id)s/templates',
)

sync_guild_template = HTTPEndpoint(
    'PUT',
    BASE_API_URL + '/guilds/%(guild_id)s/templates/%(template_code)s',
)

modify_guild_template = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/guilds/%(guild_id)s/templates/%(template_code)s',
)

delete_guild_template = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/guilds/%(guild_id)s/templates/%(template_code)s',
)

get_me = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/users/@me',
)

get_user = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/users/%(user_id)s'
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
    BASE_API_URL + '/users/@me/guilds/%(guild_id)s',
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
    BASE_API_URL + '/channels/%(channel_id)s/webhooks',
)

get_channel_webhooks = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/channels/%(channel_id)s/webhooks',
)

get_guild_webhooks = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/channels/%(guild_id)s/webhooks',
)

get_webhook = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/webhooks/%(webhook_id)s'
)

get_webhook_with_token = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/webhooks/%(webhook_id)s/%(webhook_token)s',
)

modify_webhook = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/webhooks/%(webhook_id)s',
)

modify_webhook_with_token = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/webhooks/%(webhook_id)s/%(webhook_token)s',
)

delete_webhook = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/webhooks/%(webhook_id)s',
)

delete_webhook_with_token = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/webhooks/%(webhook_id)s/%(webhook_token)s',
)

execute_webhook = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/webhooks/%(webhook_id)s/%(webhook_token)s',
)

execute_slack_webhook = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/webhooks/%(webhook_id)s/%(webhook_token)s',
)

execute_github_webhook = HTTPEndpoint(
    'POST',
    BASE_API_URL + '/webhooks/%(webhook_id)s/%(webhook_token)s',
)

modify_webhook_message = HTTPEndpoint(
    'PATCH',
    BASE_API_URL + '/webhooks/%(webhook_id)s/%(webhook_token)s/messages/%(message_id)s',
)

delete_webhook_message = HTTPEndpoint(
    'DELETE',
    BASE_API_URL + '/webhooks/%(webhook_id)s/%(webhook_token)s/messages/%(message_id)s',
)

get_gateway = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/gateway'
)

get_gateway_bot = HTTPEndpoint(
    'GET',
    BASE_API_URL + '/gateway/bot'
)
