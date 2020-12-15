

class Guild:
    def __init__(self, *, manager, data: dict):
        self._manager = manager

        self.data = data

        self.id = data.get('id')
        print(self.id)
        self.name = data.get('name')
        self.description = data.get('description')
        self.owner_id = data.get('owner_id')
        self.region = data.get('region')
        self.features = data.get('features')

        self.afk_channel_id = data.get('afk_channel_id')
        self.afk_timeout = data.get('afk_timeout')
        self.system_channel_id = data.get('system_channel_id')
        self.verification_level = data.get('verification_level')
        self.widget_enabled = data.get('widget_enabled')
        self.widget_channel_id = data.get('widget_channel_id')

        self.default_message_notifications = data.get('default_message_notifications')
        self.mfa_level = data.get('mfa_level')
        self.explicit_content_filter = data.get('explicit_content_filter')
        self.max_presences = data.get('max_presences')
        self.max_members = data.get('max_members')
        self.max_video_channel_users = data.get('max_video_channel_users')

        self.vanity_url = data.get('vanity_url_code')
        self.premium_tier = data.get('premium_tier')
        self.premium_subscription_count = data.get('premium_subscription_count')
        self.system_channel_flags = data.get('system_channel_flags')
        self.preferred_locale = data.get('preferred_locale')

        self.rules_channel_id = data.get('rules_channel_id')
        self.public_updates_channel_id = data.get('public_updates_channel_id')

        self.emojis = data.get('emojis')
        self.roles = data.get('roles')

        self.member_count = data.get('approximate_member_count')
        self.presence_count = data.get('approximate_presence_count')