from collections import namedtuple

from .client import Client
from .. import rest
from ..ws.basews import WebSocketWorker
from ..ws.shardws import Shard

_base_fields = ('shard', 'payload')

ChannnelCreateEvent = namedtuple(
    'ChannelCreateEvent', _base_fields + ('channel',))
ChannelUpdateEvent = namedtuple(
    'ChannelUpdateEvent', _base_fields + ('channel',))
ChannelDeleteEvent = namedtuple(
    'ChannelDeleteEvent', _base_fields + ('channel',))
ChannelPinsUpdateEvent = namedtuple(
    'ChannelPinsUpdateEvent', _base_fields + ('channel',))

GuildReceiveEvent = namedtuple(
    'GuildReceiveEvent', _base_fields + ('guild',))
GuildAvailableEvent = namedtuple(
    'GuildAvailableEvent', _base_fields + ('guild',))
GuildJoinEvent = namedtuple(
    'GuildJoinEvent', _base_fields + ('guild',))
GuildUpdateEvent = namedtuple(
    'GuildUpdateEvent', _base_fields + ('guild',))
GuildUnavailableEvent = namedtuple(
    'GuildUnavailableEvent', _base_fields + ('guild',))
GuildDeleteEvent = namedtuple(
    'GuildDeleteEvent', _base_fields + ('guild',))

GuildBanAddEvent = namedtuple(
    'GuildBanAddEvent', _base_fields + ('guild', 'ban',))
GuildBanRemoveEvent = namedtuple(
    'GuildBanRemoveEvent', _base_fields + ('guild', 'ban',))

GuildEmojisUpdateEvent = namedtuple(
    'GuildEmojisUpdate',  _base_fields + ('guild',))

GuildIntegrationsUpdateEvent = namedtuple(
    'GuildIntegrationsUpdateEvent', _base_fields + ('guild',))

GuildMemberAddEvent = namedtuple(
    'GuildMemberAddEvent', _base_fields + ('guild', 'member',))
GuildMemberUpdateEvent = namedtuple(
    'GuildMemberUpdateEvent', _base_fields + ('guild', 'member'))
GuildMemberRemoveEvent = namedtuple(
    'GuildMemberRemoveEvent', _base_fields + ('user', 'guild', 'member'))

GuildRoleCreateEvent = namedtuple(
    'GuildRoleCreateEvent', _base_fields + ('guild', 'role'))
GuildRoleUpdateEvent = namedtuple(
    'GuildRoleUpdateEvent', _base_fields + ('guild', 'role'))
GuildRoleDeleteEvent = namedtuple(
    'GuildRoleDeleteEvent', _base_fields + ('guild', 'role'))

IntegrationCreateEvent = namedtuple(
    'IntegrationCreateEvent', _base_fields + ('guild',))
IntegrationUpdateEvent = namedtuple(
    'IntegrationUpdateEvent', _base_fields + ('guild',))
IntegrationDeleteEvent = namedtuple(
    'IntegrationDeleteEvent', _base_fields + ('guild',))

InviteCreateEvent = namedtuple(
    'InviteCreateEvent', _base_fields + ('intive',))
InviteDeleteEvent = namedtuple(
    'InviteDeleteEvent', _base_fields + ('invite',))

MessageCreateEvent = namedtuple(
    'MessageCreateEvent', _base_fields + ('channel', 'message'))
MessageUpdateEvent = namedtuple(
    'MessageUpdateEvent', _base_fields + ('channel', 'message'))
MessageDeleteEvent = namedtuple(
    'MessageDeleteEvent', _base_fields + ('channel', 'message'))
MessageDeleteBulkEvent = namedtuple(
    'MessageDeleteBulkEvent', _base_fields + ('channel', 'messages'))

MessageReactionAddEvent = namedtuple(
    'MessageReactionAddEvent',
    _base_fields + ('channel', 'message', 'reactions', 'user'))
MessageReactionRemoveEvent = namedtuple(
    'MessageReactionRemoveEvent',
    _base_fields + ('channel', 'message', 'reactions', 'user'))
MessageReactionRemoveAllEvent = namedtuple(
    'MessageReactionRemoveAllEvent',
    _base_fields + ('channel', 'message'))
MessageReactionRemoveEmojiEvent = namedtuple(
    'MessageReactionRemoveEmoji',
    _base_fields + ('channel', 'message', 'reactions'))

TypingStartEvent = namedtuple(
    'TypingStartEvent',
    _base_fields + ('channel', 'user', 'member', 'timestamp'))

UserUpdateEvent = namedtuple(
    'UserUpdateEvent', _base_fields + ('user',))

StageInstanceCreateEvent = namedtuple(
    'StageInstanceCreateEvent', _base_fields + ('stage',))
StageInstanceUpdateEvent = namedtuple(
    'StageInstanceUpdateEvent', _base_fields + ('stage',))
StageInstanceDeleteEvent = namedtuple(
    'StageInstanceDeleteEvent', _base_fields + ('stage',))


class WebSocketClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.shards = {}
        self.sharder = WebSocketWorker(manager=self.manager, timeout=30)

        self.manager.__events__ = {}

        event_prefix = '_event_'
        for name in dir(self):
            if name.startswith(event_prefix):
                event_name = name[len(event_prefix):]
                self.manager.__events__[event_name] = getattr(self, name)

    @property
    def user(self):
        if not self.shards:
            return None
        return self.shards[0].user

    def _event_channel_create(self, shard, payload):
        channel = self.channels.upsert(payload)
        return ChannelUpdateEvent(shard=shard, payload=payload,
                                  channel=channel)

    def _event_channel_update(self, shard, payload):
        channel = self.channels.upsert(payload)
        return ChannelUpdateEvent(shard=shard, payload=payload,
                                  channel=channel)

    def _event_channel_delete(self, shard, payload):
        channel = self.channels.upsert(payload)
        channel._delete()
        return ChannelUpdateEvent(shard=shard, payload=payload,
                                  channel=channel)

    def _event_channel_pins_update(self, shard, payload):
        channel = self.channels.get(payload['channel_id'])
        if channel is not None:
            channel.last_pin_timestamp = None
        return ChannelPinsUpdateEvent(shard=shard, payload=payload,
                                      channel=channel)

    def _event_guild_receive(self, shard, payload):
        guild = self.guilds.upsert(payload)
        return GuildReceiveEvent(shard=shard, payload=payload, guild=guild)

    def _event_guild_available(self, shard, payload):
        guild = self.guilds.upsert(payload)
        return GuildAvailableEvent(shard=shard, payload=payload, guild=guild)

    def _event_guild_unavailable(self, shard, payload):
        guild = self.guilds.upsert(payload)
        return GuildUnavailableEvent(shard=shard, payload=payload, guild=guild)

    def _event_guild_delete(self, shard, payload):
        guild = self.guilds.upsert(payload)
        return GuildDeleteEvent(shard=shard, payload=payload, guild=guild)

    def _event_guild_ban_add(self, shard, payload):
        ban = None
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            ban = guild.bans.upsert(payload)

        return GuildBanAddEvent(shard=shard, payload=payload,
                                guild=guild, ban=ban)

    def _event_guild_ban_remove(self, shard, payload):
        ban = None
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            ban = guild.bans.upsert(payload)
            ban._delete()

        return GuildBanRemoveEvent(shard=shard, payload=payload,
                                   guild=guild, ban=ban)

    def _event_guild_emojis_update(self, shard, payload):
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            guild._update_emojis(payload['emojis'])

        return GuildEmojisUpdateEvent(shard=shard, payload=payload,
                                      guild=guild)

    def _event_guild_member_add(self, shard, payload):
        member = None
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            member = guild.members.upsert(payload)

        return GuildMemberAddEvent(shard=shard, payload=payload,
                                   guild=guild, member=member)

    def _event_guild_member_update(self, shard, payload):
        member = None
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            member = guild.members.upsert(payload)

        return GuildMemberUpdateEvent(shard=shard, payload=payload,
                                      guild=guild, member=member)

    def _event_guild_member_remove(self, shard, payload):
        member = None
        user = self.users.upsert(payload['user'])
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            member = guild.members.get(user.id)
            if member is not None:
                member._delete()

        return GuildMemberRemoveEvent(shard=shard, payload=payload,
                                      user=user, guild=guild,
                                      member=member)

    def _event_guild_role_create(self, shard, payload):
        role = None
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            role = guild.roles.upsert(payload)

        return GuildRoleCreateEvent(shard=shard, payload=payload,
                                    guild=guild, role=role)

    def _event_guild_role_update(self, shard, payload):
        role = None
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            role = guild.roles.upsert(payload)

        return GuildRoleUpdateEvent(shard=shard, payload=payload,
                                    guild=guild, role=role)

    def _event_guild_role_delete(self, shard, payload):
        role = None
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            role = guild.roles.get(payload['role_id'])
            if role is not None:
                role._delete()

        return GuildRoleDeleteEvent(shard=shard, payload=payload,
                                    guild=guild, role=role)

    def _event_invite_create(self, shard, payload):
        invite = self.invites.upsert(payload)
        return InviteCreateEvent(shard=shard, payload=payload, invite=invite)

    def _event_invite_delete(self, shard, payload):
        invite = self.invites.get(payload['code'])
        if invite is not None:
            invite._delete()

        return InviteDeleteEvent(shard=shard, payload=payload, invite=invite)

    def _event_message_create(self, shard, payload):
        message = None
        channel = self.channels.get(payload['channel_id'])
        if channel is not None:
            message = channel.messages.upsert(payload)

        return MessageCreateEvent(shard=shard, payload=payload,
                                  channel=channel, message=message)

    def _event_message_update(self, shard, payload):
        message = None
        channel = self.channels.get(payload['channel_id'])
        if channel is not None:
            message = channel.messages.upsert(payload)

        return MessageUpdateEvent(shard=shard, payload=payload,
                                  channel=channel, message=message)

    def _event_message_delete(self, shard, payload):
        message = None
        channel = self.channels.get(payload['channel_id'])
        if channel is not None:
            message = channel.messages.get(payload['id'])
            if message is not None:
                message._delete()

        return MessageDeleteEvent(shard=shard, payload=payload,
                                  channel=channel, message=message)

    def _event_stage_instance_create(self, shard, payload):
        stage = self.stages.upsert(payload)
        return StageInstanceCreateEvent(shard=shard, payload=payload,
                                        stage=stage)

    def _event_stage_instance_update(self, shard, payload):
        stage = self.stages.upsert(payload)
        return StageInstanceUpdateEvent(shard=shard, payload=payload,
                                        stage=stage)

    def _event_state_instance_delete(self, shard, payload):
        stage = self.stages.upsert(payload)
        stage._delete()
        return StageInstanceCreateEvent(shard=shard, payload=payload,
                                        stage=stage)

    async def fetch_gateway(self):
        data = await rest.get_gateway.request(session=self.manager.rest)
        return data

    async def connect(self, *args, **kwargs):
        gateway = await self.fetch_gateway()

        shard = await self.sharder.create_connection(
            Shard, gateway['url'], *args, **kwargs)

        self.shards[0] = shard

        await self.sharder.work()

    def run_forever(self):
        self.manager.loop.create_task(self.connect())
        self.manager.run_forever()
