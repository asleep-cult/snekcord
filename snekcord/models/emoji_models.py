from .base_models import BaseModel
from .. import json
from ..collection import Collection

__all__ = ('CustomEmoji',)


class CustomEmoji(BaseModel):
    name = json.JSONField('name')
    require_colons = json.JSONField('require_colons')
    managed = json.JSONField('managed')
    animated = json.JSONField('animated')
    available = json.JSONField('available')

    def __init__(self, *, state, user) -> None:
        super().__init__(state=state)
        self.user = user
        self.roles = Collection()

    def __str__(self) -> str:
        if self.animated:
            return f'<a:{self.name}:{self.id}>'
        else:
            return f'<:{self.name}:{self.id}>'

    @property
    def guild(self):
        return self.state.guild

    def _update_roles(self, roles):
        self.roles.clear()

        for role in roles:
            wrapper = self.guild.roles.wrap_id(role)
            self.roles.set(wrapper.id, wrapper)
