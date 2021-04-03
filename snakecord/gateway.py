from typing import Optional

from .connection import Shard
from .events import EventPusher
from .client import Client

class BaseGatewayEvent:
    def __init__(self, sharder: 'Sharder', payload: Optional[dict] = None):
        self.sharder = sharder
        self.client = sharder.client
        self.payload = payload


class ShardReadyReceiveEvent(BaseGatewayEvent):
    name = 'shard_ready_receive'

    def __init__(self, sharder: 'Sharder', shard: Shard, payload: dict):
        super().__init__(sharder, payload)
        self.shard = shard
        self.client.user = self.client.users.append(payload['user'])


class ShardReadyEvent(BaseGatewayEvent):
    name = 'shard_ready'

    def __init__(self, sharder: 'Sharder', shard: Shard):
        super().__init__(sharder)
        self.shard = shard


class ChannelCreateEvent(BaseGatewayEvent):
    name = 'channel_create'

    def __init__(self, sharder: 'Sharder', payload: dict):
        super().__init__(sharder, payload)
        self.channel = self.client.channels.append(payload)


class ChannelUpdateEvent(BaseGatewayEvent):
    name = 'channel_update'

    def __init__(self, sharder: 'Sharder', payload: dict):
        super().__init__(sharder, payload)
        self.channel = self.client.channels.append(payload)


class ChannelDeleteEvent(BaseGatewayEvent):
    name = 'channel_delete'

    def __init__(self, sharder: 'Sharder', payload: dict):
        super().__init__(sharder, payload)
        self.channel = self.client.channels.pop(payload['id'])


class ChannelPinsUpdateEvent(BaseGatewayEvent):
    name = 'channel_pins_update'

    def __init__(self, sharder: 'Sharder', payload: dict):
        super().__init__(sharder, payload)
        self.channel = self.client.channels.get(payload['channel_id'])
        self.channel.last_pin_timestamp = payload['last_pin_timestamp']


class GuildCreateEvent(BaseGatewayEvent):
    name = 'guild_create'

    def __init__(self, sharder: 'Sharder', payload: dict):
        super().__init__(sharder, payload)
        self.guild = self.client.guilds.append(payload)


class GuildUpdateEvent(BaseGatewayEvent):
    name = 'guild_update'

    def __init__(self, sharder: 'Sharder', payload: dict):
        super().__init__(sharder, payload)
        self.guild = self.client.guilds.append(payload)


class GuildDeleteEvent(BaseGatewayEvent):
    name = 'guild_delete'

    def __init__(self, sharder: 'Sharder', payload: dict):
        super().__init__(sharder, payload)
        self.guild = self.client.guilds.pop(payload['id'])


class GuildBanAddEvent(BaseGatewayEvent):
    name = 'guild_ban_add'

    def __init__(self, sharder: 'Sharder', payload: dict):
        super().__init__(sharder, payload)
        self.guild = self.client.guilds.get(payload['guild_id'])
        self.ban = self.guild.bans.append(payload)


class GuildBanRemoveEvent(BaseGatewayEvent):
    name = 'guild_ban_remove'

    def __init__(self, sharder: 'Sharder', payload: dict):
        super().__init__(sharder, payload)
        self.guild = self.client.guilds.get(payload['guild_id'])
        self.client.users.append(payload['user'])  # maybe the user was updated?
        self.ban = self.guild.bans.pop(payload['user']['id'])


class GuildEmojisUpdateEvent(BaseGatewayEvent):
    name = 'guild_emojis_update'

    def __init__(self, sharder: 'Sharder', payload: dict):
        super().__init__(sharder, payload)
        self.guild = self.client.guilds.get(payload['guild_id'])
        self.guild.emojis.clear()
        self.emojis = self.guild.emojis

        for emoji in payload['emojis']:
            self.guild.emojis.append(emoji)


class GuildMemberAddEvent(BaseGatewayEvent):
    name = 'guild_member_add'

    def __init__(self, sharder: 'Sharder', payload: dict):
        super().__init__(sharder, payload)
        self.guild = self.client.guilds.get(payload['guild_id'])
        self.member = self.guild.members.append(payload)


class GuildMemberUpdateEvent(BaseGatewayEvent):
    name = 'guild_member_update'

    def __init__(self, sharder: 'Sharder', payload: dict):
        super().__init__(sharder, payload)
        self.guild = self.client.guilds.get(payload['guild_id'])
        self.member = self.guild.members.append(payload)


class GuildMemberRemoveEvent(BaseGatewayEvent):
    name = 'guild_member_remove'

    def __init__(self, sharder: 'Sharder', payload: dict):
        super().__init__(sharder, payload)
        self.guild = self.client.guilds.get(payload['guild_id'])
        user = self.client.users.append(payload['user'])  # maybe the user was updated?
        self.member = self.guild.members.pop(user.id)


class MessageCreateEvent(BaseGatewayEvent):
    name = 'message_create'

    def __init__(self, sharder: 'Sharder', payload: dict):
        super().__init__(sharder, payload)
        self.channel = sharder.client.channels.get(payload['channel_id'])
        self.message = self.channel.messages.append(payload)


class Sharder(EventPusher):
    handlers = (
        ShardReadyReceiveEvent, ShardReadyEvent, ChannelCreateEvent,
        ChannelUpdateEvent, ChannelDeleteEvent, ChannelPinsUpdateEvent,
        GuildCreateEvent, GuildUpdateEvent, GuildDeleteEvent,
        GuildBanAddEvent, GuildBanRemoveEvent, GuildEmojisUpdateEvent,
        GuildMemberAddEvent, GuildMemberUpdateEvent, GuildMemberRemoveEvent,
        MessageCreateEvent
    )

    def __init__(self, client: Client, *, max_shards: Optional[int] = None, intents: Optional[int] = None):
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
