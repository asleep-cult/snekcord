from .base import BaseObject
from ..utils import JsonField


class User(BaseObject):
    __json_fields__ = {
        'name': JsonField('username'),
        'discriminator': JsonField('discriminator'),
        'avatar': JsonField('avatar'),
        'bot': JsonField('bot'),
        'system': JsonField('system'),
        'mfa_enabled': JsonField('mfa_enabled'),
        'locale': JsonField('locale'),
        'verified': JsonField('verified'),
        'email': JsonField('email'),
        'flags': JsonField('flags'),
        'premium_type': JsonField('premium_type'),
        'public_flags': JsonField('public_flags'),
    }
