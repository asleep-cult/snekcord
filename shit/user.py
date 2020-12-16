from .utils import (
    JsonStructure,
    JsonField
)

class User(JsonStructure):

    id: int = JsonField(int, 'id')
    name: str = JsonField(str, 'name')
    discriminator: str = JsonField(str, 'discriminator')
    bot: bool = JsonField(bool, 'bot')
    system: bool = JsonField(bool, 'system')

    def __init__(self, *, manager):
        self._manager = manager
