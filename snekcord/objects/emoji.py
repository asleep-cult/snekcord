from .base import SnowflakeObject
from .. import json
from ..collection import Collection

__all__ = ('CustomEmoji',)


class CustomEmoji(SnowflakeObject):
    __slots__ = ('user', 'roles')

    name = json.JSONField('name')
    require_colons = json.JSONField('require_colons')
    managed = json.JSONField('managed')
    animated = json.JSONField('animated')
    available = json.JSONField('available')

    def __init__(self, *, state) -> None:
        super().__init__(state=state)
        self.user = None
        self.roles = Collection()

    @property
    def guild(self):
        return self.state.guild

    def __str__(self) -> str:
        if self.animated:
            return f'<a:{self.name}:{self.id}>'
        else:
            return f'<:{self.name}:{self.id}>'

    async def update_user(self, data):
        self.user = await self.client.users.upsert(data)

    async def update_roles(self, roles):
        self.roles.clear()

        for role in roles:
            role = self.guild.roles.wrap_id(role)
            self.roles[role.id] = role
