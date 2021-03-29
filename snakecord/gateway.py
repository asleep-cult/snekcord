from .connection import Shard
from .events import EventPusher


class BaseGatewayEvent:
    def __init__(self, sharder, payload):
        self.client = sharder.client
        self.payload = payload


class ShardReadyReceiveHandler(BaseGatewayEvent):
    name = 'shard_ready_receive'

    def __init__(self, sharder, shard, payload):
        super().__init__(sharder, payload)
        self.shard = shard
        sharder.client.user = sharder.client.users.append(payload['user'])


class ChannelCreateHandler(BaseGatewayEvent):
    name = 'channel_create'

    def __init__(self, sharder, payload):
        super().__init__(sharder, payload)
        self.channel = sharder.client.channels.append(payload)


class ChannelUpdateHandler(BaseGatewayEvent):
    name = 'channel_update'

    def __init__(self, sharder, payload):
        super().__init__(sharder, payload)
        self.channel = sharder.client.channels.append(payload)


class ChannelDeleteHandler(BaseGatewayEvent):
    name = 'channel_delete'

    def __init__(self, sharder, payload):
        super().__init__(sharder, payload)
        self.channel = sharder.client.channels.pop(payload['id'])


class ChannelPinsUpdateHandler(BaseGatewayEvent):
    name = 'channel_pins_update'

    def __init__(self, sharder, payload):
        super().__init__(sharder, payload)
        self.channel = sharder.client.channels.get(payload['channel_id'])
        self.channel.last_pin_timestamp = payload['last_pin_timestamp']


class GuildCreateHandler(BaseGatewayEvent):
    name = 'guild_create'

    def __init__(self, sharder, payload):
        super().__init__(sharder, payload)
        self.guild = sharder.client.guilds.append(payload)


class GuildUpdateHandler(BaseGatewayEvent):
    name = 'guild_update'

    def __init__(self, sharder, payload):
        super().__init__(sharder, payload)
        self.guild = sharder.client.guilds.append(payload)


class GuildDeleteHandler(BaseGatewayEvent):
    name = 'guild_delete'

    def __init__(self, sharder, payload):
        super().__init__(sharder, payload)
        self.guild = sharder.client.guilds.pop(payload['id'])


class MessageCreateHandler(BaseGatewayEvent):
    name = 'message_create'

    def __init__(self, sharder, payload):
        super().__init__(sharder, payload)
        self.channel = sharder.client.channels.get(payload['channel_id'])
        self.message = self.channel.messages.append(payload)


class Sharder(EventPusher):
    handlers = (
        ShardReadyReceiveHandler, ChannelCreateHandler, ChannelUpdateHandler,
        ChannelDeleteHandler, ChannelPinsUpdateHandler, GuildCreateHandler,
        GuildUpdateHandler, GuildDeleteHandler, MessageCreateHandler
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
            shard = Shard(shard_id, self.gateway_data['url'], self)
            self.shards[shard_id] = shard

        for shard in self.shards.values():
            await shard.connect(port=443, ssl=True)
