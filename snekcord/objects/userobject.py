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
    @property
    def mention(self):
        return f'<@{self.id}>'
    
    @property
    def username(self):
        return self.username
    
    @property
    def discriminator(self):
        return self.discriminator
    
    @property
    def id(self):
        return self.id
    
    @property
    def bot(self):
        return self.bot
    


