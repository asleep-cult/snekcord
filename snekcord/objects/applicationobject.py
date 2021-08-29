from .teamobject import Team
from ..flags import ApplicationFlags
from ..json import JsonArray, JsonField, JsonObject
from ..snowflake import Snowflake


class Application(JsonObject):
    id = JsonField('id', Snowflake)
    name = JsonField('name')
    description = JsonField('description')
    rpc_origins = JsonArray('rpc_origins')
    bot_public = JsonField('bot_public')
    bot_require_code_grant = JsonField('bot_require_code_grant')
    terms_of_service_url = JsonField('terms_of_service_url')
    privacy_policy_url = JsonField('privacy_policy_url')
    summary = JsonField('summary')
    verify_key = JsonField('verify_key')
    guild_id = JsonField('guild_id', Snowflake)
    primary_sku_id = JsonField('primary_sku_id', Snowflake)
    slug = JsonField('slug')
    flags = JsonField('falgs', ApplicationFlags.from_value)

    def __init__(self, *, client):
        self.client = client
        self.owner = None
        self.team = None

    @property
    def guild(self):
        return self.client.guilds.get(self.guild_id)

    def update(self, data):
        super().update(data)

        if 'owner' in data:
            self.owner = self.client.users.upsert(data['user'])

        if 'team' in data:
            self.team = Team.unmarshal(data['team'], applciation=self)

        return self
