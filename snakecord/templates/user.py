from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseTemplate
from ..utils.json import JsonField, JsonTemplate

if TYPE_CHECKING:
    from ..objects.user import User

UserTemplate: JsonTemplate[User] = JsonTemplate(
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
