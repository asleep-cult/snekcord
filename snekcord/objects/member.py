from datetime import datetime

from .base import SnowflakeObject
from .. import json

__all__ = ('Member',)


class Member(SnowflakeObject):
    nick = json.JSONField('nick')
    avatar = json.JSONField('avatar')
    joined_at = json.JSONField('joined_at', datetime.fromisoformat)
    premium_since = json.JSONField('permium_since', datetime.fromisoformat)
    deaf = json.JSONField('deaf')
    mute = json.JSONField('mute')
    pending = json.JSONField('pending')
    # permissions
