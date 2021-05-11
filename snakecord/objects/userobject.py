from .baseobject import BaseObject
from ..templates import UserTemplate


class User(BaseObject, template=UserTemplate):
    @property
    def mention(self):
        return f'<@{self.id}>'
