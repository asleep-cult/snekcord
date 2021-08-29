from .emojiobject import CustomEmoji, PartialCustomEmoji, PartialUnicodeEmoji, UnicodeEmoji
from .. import http
from ..json import JsonField, JsonObject
from ..snowflake import Snowflake
from ..undefined import undefined

__all__ = ('WelcomeScreen', 'WelcomeScreenChannel')


class WelcomeScreen(JsonObject):
    __slots__ = ('guild', 'welcome_channels')

    channel_id = JsonField('channel_id', Snowflake)

    def __init__(self, *, guild):
        self.guild = guild
        self.welcome_channels = {}

    async def fetch(self):
        data = await http.get_guild_welcome_screen.request(
            self.guild.state.client.http, guild_id=self.guild.id
        )

        return self.update(data)

    async def modify(self, *, enabled=undefined, welcome_channels=undefined, description=undefined):
        json = {}

        if enabled is not undefined:
            if enabled is not None:
                json['enabled'] = bool(enabled)
            else:
                json['enabled'] = None

        if welcome_channels is not undefined:
            if welcome_channels is not None:
                json['welcome_channels'] = []

                for channel, data in welcome_channels.items():
                    welcome_channel = {'channel': Snowflake.try_snowflake(channel)}

                    if 'description' in data:
                        description = data['description']

                        if description is not None:
                            welcome_channel['description'] = str(description)
                        else:
                            welcome_channel['description'] = None

                    if 'emoji' in data:
                        emoji = self.guild.state.client.emojis.resolve(data['emoji'])

                        if isinstance(emoji, (UnicodeEmoji, PartialUnicodeEmoji)):
                            welcome_channel['emoji_name'] = emoji.unicode

                        elif isinstance(emoji, (CustomEmoji, PartialCustomEmoji)):
                            welcome_channel['emoji_name'] = emoji.name
                            welcome_channel['emoji_id'] = emoji.id

                    json['welcome_channels'].append(welcome_channel)
            else:
                json['welcome_channels'] = None

        if 'description' in data:
            description = data['description']

            if description is not None:
                json['description'] = str(description)
            else:
                json['description'] = None

        data = await http.modify_guild_welcome_screen.request(
            self.guild.state.client.http, guild_id=self.guild.id, json=json
        )

        return self.update(data)

    def update(self, data):
        super().update(data)

        if 'welcome_channels' in data:
            welcome_channels = set()

            for welcome_channel in data['welcome_channels']:
                channel = self.welcome_channels.get(welcome_channel['channel_id'])

                if channel is not None:
                    channel.update(welcome_channel)
                else:
                    channel = WelcomeScreenChannel.unmarshal(welcome_channel, welcome_screen=self)

                welcome_channels.add(channel.channel_id)

            for channel_id in set(self.welcome_channels.keys()) - welcome_channels:
                del self.welcome_channels[channel_id]

        return self


class WelcomeScreenChannel(JsonObject):
    __slots__ = ('welcome_screen',)

    channel_id = JsonField('channel_id', Snowflake)
    description = JsonField('description')
    emoji_id = JsonField('emoji', Snowflake)
    emoji_name = JsonField('emoji_name')

    def __init__(self, *, welcome_screen):
        self.welcome_screen = welcome_screen

    @property
    def channel(self):
        return self.welcome_screen.guild.channels.get(self.channel_id)

    @property
    def emoji(self):
        return self.welcome_screen.guild.emojis.get(self.emoji_id)
