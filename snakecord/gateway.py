from .connection import Shard
from .events import EventPusher


class BaseGatewayEvent:
    def __init__(self, sharder, payload):
        self.client = sharder.client
        self.payload = payload


class ChannelCreateHandler(BaseGatewayEvent):
    name = 'channel_create'

    def __init__(self, sharder, payload, channel):
        super().__init__(sharder, payload)
        self.channel = channel

    @classmethod
    def _execute(cls, sharder, payload):
        channel = sharder.client.channels._add(payload)
        return cls(sharder, payload, channel)


class ChannelUpdateHandler(BaseGatewayEvent):
    name = 'channel_update'

    def __init__(self, sharder, payload, channel):
        super().__init__(sharder, payload)
        self.channel = channel

    @classmethod
    def _execute(cls, sharder, payload):
        channel = sharder.client.channels._add(payload)
        return cls(sharder, payload, channel)


class ChannelDeleteHandler(BaseGatewayEvent):
    name = 'channel_delete'

    def __init__(self, sharder, payload, channel):
        super().__init__(sharder, payload)
        self.channel = channel

    @classmethod
    def _execute(cls, sharder, payload):
        channel = sharder.client.channels.pop(payload['id'])
        return cls(sharder, payload, channel)


class ChannelPinsUpdateHandler(BaseGatewayEvent):
    name = 'channel_pins_update'

    def __init__(self, sharder, payload, channel):
        super().__init__(sharder, payload)
        self.channel = channel

    @classmethod
    def _execute(cls, sharder, payload):
        channel = sharder.client.channels.get(payload['channel_id'])
        channel.last_pin_timestamp = payload['last_pin_timestamp']
        return cls(sharder, payload, channel)


class GuildCreateHandler(BaseGatewayEvent):
    name = 'guild_create'

    def __init__(self, sharder, payload, guild):
        super().__init__(sharder, payload)
        self.guild = guild

    @classmethod
    def _execute(cls, sharder, payload):
        guild = sharder.client.guilds._add(payload)
        return cls(sharder, payload, guild)


class GuildUpdateHandler(BaseGatewayEvent):
    name = 'guild_update'

    def __init__(self, sharder, payload, guild):
        super().__init__(sharder, payload)
        self.guild = guild

    @classmethod
    def _execute(cls, sharder, payload):
        guild = sharder.client.guilds._add(payload)
        return cls(sharder, payload, guild)


class GuildDeleteHandler(BaseGatewayEvent):
    name = 'guild_delete'

    def __init__(self, sharder, payload, guild):
        super().__init__(sharder, payload)
        self.guild = guild

    @classmethod
    def _execute(cls, sharder, payload):
        guild = sharder.client.guilds.pop(payload['id'])
        return cls(sharder, payload, guild)


class MessageCreateHandler(BaseGatewayEvent):
    name = 'message_create'

    def __init__(self, sharder, payload, message):
        super().__init__(sharder, payload)
        self.message = message

    @classmethod
    def _execute(cls, sharder, payload):
        channel = sharder.client.channels.get(payload['channel_id'])
        message = channel.messages._add(payload)
        return cls(sharder, payload, message)


class Sharder(EventPusher):
    handlers = (
        ChannelCreateHandler, ChannelUpdateHandler, ChannelDeleteHandler,
        ChannelPinsUpdateHandler, GuildCreateHandler, GuildUpdateHandler,
        GuildDeleteHandler, MessageCreateHandler
    )

    def __init__(self, client, *, max_shards=None, intents=None):
        super().__init__(client.loop)

        self.client = client
        self.max_shards = max_shards
        self.multi_sharded = self.max_shards > 1
        self.intents = intents
        self.shards = {}
        self.gateway_data = None
        self.token = None

    async def connect(self):
        self.token = self.client.token
        self.gateway_data = await self.client.rest.get_gateway_bot()

        shards = min((self.max_shards, self.gateway_data['shards']))

        for shard_id in range(shards):
            shard = Shard(self, self.gateway_data['url'], shard_id)
            self.shards[shard_id] = shard

        for shard in self.shards.values():
            await shard.connect()
