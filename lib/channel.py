import json
from . import HTTPClient

class GuildChannel:
    def __init__(self, data : dict):
        self.data = data

        self.id = int(data['id'])
        self.name = data['name']
        self.guild_id = data['guild_id']
        self.permission_overwrites = data['permission_overwrites']
        self.position = data['position']

        self.nsfw = data['nsfw']
        self.parent_id = data['parent_id']
        self.type = data['type']

        self.http = HTTPClient()

    def __str__(self):
        return json.dumps(self.data, indent=4)

    async def delete(self):
        data = await self.http.delete_channel(self.id)
        return data

    async def edit(self, *, reason=None, **options):
        data = await self.http.edit_channel(self.id, reason=reason, **options)
        return data

    @property
    def mention(self):
        return '<#{0}>'.format(self.id)

    def raw_data(self):
        return self.data

class TextChannel(GuildChannel):
    def __init__(self, data):
        self.data = data
        super(TextChannel, self).__init__(data)

        self.last_message_id = data['last_message_id']

    async def send(self, *args, **kwargs):
        data = await self.http.send_message(self.id, *args, **kwargs)
        return data

    async def get_message(self, message_id):
        data = await self.http.get_message(self.id, message_id)
        return data

class VoiceChannel(GuildChannel):
    def __init__(self, data):
        super(VoiceChannel, self).__init__(data)
        self.data = data

        self.bitrate = data['bitrate']
        self.user_limit = data['user_limit']

class CategoryChannel(GuildChannel):
    def __init__(self, data):
        super(CategoryChannel, self).__init__(data)
        self.data = data

class DMChannel:
    def __init__(self, data : dict):
        self.data = data

        self.last_message_id = data['last_message_id']
        self.id = data['id']
        self.type = data['type']

        self.recepients = data['recepients']
        self.recepient_username = self.recepients[0]['username']
        self.recepient_discriminator = self.recepients[0]['discriminator']
        self.recepient_id = self.recepients[0]['id']

