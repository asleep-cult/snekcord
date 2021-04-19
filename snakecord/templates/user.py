from .template import BaseTemplate
from ..utils.json import JsonField, JsonTemplate

UserTemplate = JsonTemplate(
    name=JsonField('username'),
    discriminator=JsonField('discriminator'),
    avatar=JsonField('avatar'),
    bot=JsonField('bot'),
    system=JsonField('system'),
    mfa_enabled=JsonField('mfa_enabled'),
    locale=JsonField('locale'),
    verified=JsonField('verified'),
    email=JsonField('email'),
    flags=JsonField('flags'),
    premium_type=JsonField('premium_type'),
    public_flags=JsonField('public_flags'),
    __extends__=(BaseTemplate,)
)
