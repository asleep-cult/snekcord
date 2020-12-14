from .http import HTTPClient
from .user import User

class Guild:
    def __init__(self, data : dict, *, with_counts=False):
        self.data = data
        self._http = HTTPClient()

        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.owner_id = data['owner_id']
        self.region = data['region']
        self.features = data['features']

        self.afk_channel_id = data['afk_channel_id']
        self.afk_timeout = data['afk_timeout']
        self.system_channel_id = data['system_channel_id']
        self.verification_level = data['verification_level']
        self.widget_enabled = data['widget_enabled']
        self.widget_channel_id = data['widget_channel_id']

        self.default_message_notifications = data['default_message_notifications']
        self.mfa_level = data['mfa_level']
        self.explicit_content_filter = data['explicit_content_filter']
        self.max_presences = data['max_presences']
        self.max_members = data['max_members']
        self.max_video_channel_users = data['max_video_channel_users']

        self.vanity_url = data['vanity_url_code']
        self.premium_tier = data['premium_tier']
        self.premium_subscription_count = data['premium_subscription_count']
        self.system_channel_flags = data['system_channel_flags']
        self.preferred_locale = data['preferred_locale']

        self.rules_channel_id = data['rules_channel_id']
        self.public_updates_channel_id = data['public_updates_channel_id']

        self.emojis = data['emojis']
        self.roles = data['roles']

        if with_counts:
            self.member_count = data['approximate_member_count']
            self.presence_count = data['approximate_presence_count']

    async def delete(self):
        data = await self._http.delete_guild(self.id)
        return data

    async def get_member(self, user_id):
        data = await self._http.get_guild_member(self.id, user_id)
        return data

    async def create_role(self, **kwargs):
        data = await self._http.create_guild_role(self.id, **kwargs)
        return data

    async def delete_role(self, role_id):
        data = await self._http.delete_guild_role(self.id, role_id)
        return data

    async def add_roles(self, user_id, role_id):
        data = await self._http.add_member_role(self.id, user_id, role_id)
        return data

    async def remove_roles(self, user_id, role_id):
        data = await self._http.remove_member_role(self.id, user_id, role_id)
        return data

    async def bans(self):
        data = await self._http.get_guild_bans(self.id)
        return data

    async def fetch_ban(self, user_id):
        data = await self._http.get_guild_ban(self.id, user_id)
        return data

    async def ban(self, user_id, **kwargs):
        data = await self._http.ban(self.id, user_id, **kwargs)
        return data

class Member(User):
    def __init__(self, data):
        super(Member, self).__init__(data)
        self.data = data
        self._http = HTTPClient()

        self.joined_at = data['joined_at']
        self.roles = data['roles']
        self.premium_since = data['premium_since']

    async def ban(self, guild_id, **kwargs):
        data = await self._http.ban(guild_id, self.id, **kwargs)
