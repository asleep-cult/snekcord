from .utils import (
    JsonStructure,
    JsonField
)

class GuildChannel(JsonStructure):

    id: int = JsonField(int, 'id')
    name: str = JsonField(str, 'name')
    parent_id: int = JsonField(int, 'parent_id')
    position: int = JsonField(int, 'position')
    guild_id: int = JsonField(int, 'guild_id')
    nsfw: bool = JsonField(bool, 'nsfw')
    permission_overwrites: tuple = JsonField(tuple, 'permission_overwrites')

    def __init__(self, *, manager):
        self._manager = manager

class TextChannel(GuildChannel):

    last_message_id: int = JsonField(int, 'last_messae_id')
    rate_limit_per_user: int = JsonField(int, 'rate_limit_per_user')
    topic: str = JsonField(str, 'topic')

    async def send(self, request):
        return await self._manager.rest.send_message(self.id, request)


class VoiceChannel(GuildChannel):

    bitrate: int = JsonField(int, 'bitrate')
    user_limit: int = JsonField(int, 'user_limit')


class CategoryChannel(GuildChannel):
    pass

class DMChannel(JsonStructure):

    last_message_id: int = JsonField(int, 'last_message_id')
    id: int = JsonField(int, 'id')
    type: int = JsonField(int, 'type')

    def __init__(self, *, manager):
        self._manager = manager
