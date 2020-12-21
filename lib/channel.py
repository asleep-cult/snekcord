from .utils import (
    JsonStructure,
    JsonField,
    Snowflake
)

class ChannelType:
    GUILD_TEXT = 0	
    DM = 1	
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6

class GuildChannel(JsonStructure):
    id: Snowflake = JsonField('id', Snowflake, str)
    name = JsonField('name')
    guild_id: Snowflake = JsonField('guild_id', Snowflake, str)
    permission_overwrites = JsonField('permission_overwrites')
    position = JsonField('position')
    nsfw = JsonField('nsfw')
    parent_id: Snowflake = JsonField('parent_id', Snowflake, str)
    type = JsonField('type')

    def __init__(self, manager):
        self.manager = manager

    @property
    def mention(self):
        return '<#{0}>'.format(self.id)

class TextChannel(GuildChannel):
    last_message_id = JsonField('last_message_id', int, str)

    def send(self, content=None, *, nonce=None, tts=False):
        return self.manager.rest.send_message(self.id, content, nonce, tts)

class VoiceChannel(GuildChannel):
    bitrate = JsonField('bitrate')
    user_limit = JsonField('user_limit')

class CategoryChannel(GuildChannel):
    pass

class DMChannel(JsonStructure):
    id = JsonField('id')
    last_message_id = JsonField('last_message_id', int, str)
    type = JsonField('type')
    recepients = JsonField('recepients')

    def __init__(self, manager):
        self.manager = manager
