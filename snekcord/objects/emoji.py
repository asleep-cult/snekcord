import attr

from .base import SnowflakeObject
from .. import json
from ..snowflake import Snowflake

__all__ = ('CustomEmoji',)


class CachedCustomEmoji(json.JSONObject):
    id = json.JSONField('id')
    name = json.JSONField('name')
    require_colons = json.JSONField('require_colons')
    managed = json.JSONField('managed')
    animated = json.JSONField('animated')
    available = json.JSONField('animated')
    user_id = json.JSONField('user_id')
    role_ids = json.JSONArray('role_ids')


@attr.s(kw_only=True)
class CustomEmoji(SnowflakeObject):
    name: str = attr.ib()
    require_colons: bool = attr.ib()
    managed: bool = attr.ib()
    animated: bool = attr.ib()
    available: bool = attr.ib()
    user_id: Snowflake = attr.ib()
    roles = attr.ib()

    @property
    def guild(self):
        return self.state.guild
