from .base import SnowflakeObject
from .. import json

__all__ = ('RoleTags', 'Role')


class RoleTags(json.JSONObject):
    __slots__ = ('role', 'bot', 'integration')

    premium_subscriper = json.JSONField('premium_subscriber')

    def __init__(self, *, role):
        self.role = role
        self.bot = self.client.users.wrap_id(None)
        # self.integration = self.role.guild.integrations.wrap_id(None)

    @property
    def client(self):
        return self.role.client


class Role(SnowflakeObject):
    __slots__ = ('tags',)

    name = json.JSONField('name')
    color = json.JSONField('color')
    hoist = json.JSONField('hoist')
    icon = json.JSONField('icon')
    emoji = json.JSONField('unicode_emoji')
    # permissions
    managed = json.JSONField('managed')
    mentionable = json.JSONField('mentionable')

    def __init__(self, *, state):
        super().__init__(state=state)
        self.tags = RoleTags(role=self)

    @property
    def guild(self):
        return self.state.guild

    def _update_tags(self, data):
        bot_id = data.get('bot_id')
        if bot_id is not None:
            self.tags.bot.set_id(bot_id)

        integration_id = data.get('integration_id')
        if integration_id is not None:
            self.tags.integration.set_id(integration_id)

        self.tags.update(data)
