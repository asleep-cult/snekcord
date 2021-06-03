from .baseobject import BaseObject, BaseTemplate
from ..utils import JsonField, JsonTemplate

__all__ = ('User',)


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


class User(BaseObject, template=UserTemplate):
    def __str__(self):
        return f'@{self.name}'

    @property
    def tag(self):
        return f'{self.name}#{self.id}'

    @property
    def mention(self):
        return f'<@{self.id}>'
