from .client import Client
from .. import events
from .. import rest
from ..utils.bitset import Flag, NamedBitset
from ..ws.shardws import Sharder

__all__ = ('WebSocketIntents', 'WebSocketClient')


class WebSocketIntents(NamedBitset):
    guilds = Flag(0)
    guild_members = Flag(1)
    guild_bans = Flag(2)
    guild_emojis = Flag(3)
    guild_integrations = Flag(4)
    guild_webhooks = Flag(5)
    guild_invites = Flag(6)
    guild_voice_states = Flag(7)
    guild_presences = Flag(8)
    guild_messages = Flag(9)
    guild_message_reactions = Flag(10)
    guild_message_typing = Flag(11)
    direct_messages = Flag(12)
    direct_message_reactions = Flag(13)
    direct_message_typing = Flag(14)


class WebSocketClient(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sharder = Sharder(manager=self.manager, timeout=30)

        self.manager.__events__ = {}

        event_prefix = '_event_'
        for name in dir(self):
            if name.startswith(event_prefix):
                event_name = name[len(event_prefix):]
                self.manager.__events__[event_name] = getattr(self, name)

    @property
    def shards(self):
        return self.sharder.shards

    @property
    def user(self):
        return self.sharder.user

    def _event_channel_create(self, shard, payload):
        channel = self.channels.upsert(payload)
        return events.ChannelUpdateEvent(shard=shard, payload=payload,
                                         channel=channel)

    def _event_channel_update(self, shard, payload):
        channel = self.channels.upsert(payload)
        return events.ChannelUpdateEvent(shard=shard, payload=payload,
                                         channel=channel)

    def _event_channel_delete(self, shard, payload):
        channel = self.channels.upsert(payload)
        channel._delete()
        return events.ChannelUpdateEvent(shard=shard, payload=payload,
                                         channel=channel)

    def _event_channel_pins_update(self, shard, payload):
        channel = self.channels.get(payload['channel_id'])
        if channel is not None:
            channel.last_pin_timestamp = None
        return events.ChannelPinsUpdateEvent(shard=shard, payload=payload,
                                             channel=channel)

    def _event_guild_receive(self, shard, payload):
        guild = self.guilds.upsert(payload)
        return events.GuildReceiveEvent(shard=shard, payload=payload,
                                        guild=guild)

    def _event_guild_available(self, shard, payload):
        guild = self.guilds.upsert(payload)
        return events.GuildAvailableEvent(shard=shard, payload=payload,
                                          guild=guild)

    def _event_guild_unavailable(self, shard, payload):
        guild = self.guilds.upsert(payload)
        return events.GuildUnavailableEvent(shard=shard, payload=payload,
                                            guild=guild)

    def _event_guild_delete(self, shard, payload):
        guild = self.guilds.upsert(payload)
        return events.GuildDeleteEvent(shard=shard, payload=payload,
                                       guild=guild)

    def _event_guild_ban_add(self, shard, payload):
        ban = None
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            ban = guild.bans.upsert(payload)

        return events.GuildBanAddEvent(shard=shard, payload=payload,
                                       guild=guild, ban=ban)

    def _event_guild_ban_remove(self, shard, payload):
        ban = None
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            ban = guild.bans.upsert(payload)
            ban._delete()

        return events.GuildBanRemoveEvent(shard=shard, payload=payload,
                                          guild=guild, ban=ban)

    def _event_guild_emojis_update(self, shard, payload):
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            guild._update_emojis(payload['emojis'])

        return events.GuildEmojisUpdateEvent(shard=shard, payload=payload,
                                             guild=guild)

    def _event_guild_member_add(self, shard, payload):
        member = None
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            member = guild.members.upsert(payload)

        return events.GuildMemberAddEvent(shard=shard, payload=payload,
                                          guild=guild, member=member)

    def _event_guild_member_update(self, shard, payload):
        member = None
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            member = guild.members.upsert(payload)

        return events.GuildMemberUpdateEvent(shard=shard, payload=payload,
                                             guild=guild, member=member)

    def _event_guild_member_remove(self, shard, payload):
        member = None
        user = self.users.upsert(payload['user'])
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            member = guild.members.get(user.id)
            if member is not None:
                member._delete()

        return events.GuildMemberRemoveEvent(shard=shard, payload=payload,
                                             user=user, guild=guild,
                                             member=member)

    def _event_guild_role_create(self, shard, payload):
        role = None
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            role = guild.roles.upsert(payload)

        return events.GuildRoleCreateEvent(shard=shard, payload=payload,
                                           guild=guild, role=role)

    def _event_guild_role_update(self, shard, payload):
        role = None
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            role = guild.roles.upsert(payload)

        return events.GuildRoleUpdateEvent(shard=shard, payload=payload,
                                           guild=guild, role=role)

    def _event_guild_role_delete(self, shard, payload):
        role = None
        guild = self.guilds.get(payload['guild_id'])
        if guild is not None:
            role = guild.roles.get(payload['role_id'])
            if role is not None:
                role._delete()

        return events.GuildRoleDeleteEvent(shard=shard, payload=payload,
                                           guild=guild, role=role)

    def _event_invite_create(self, shard, payload):
        invite = self.invites.upsert(payload)
        return events.InviteCreateEvent(shard=shard, payload=payload,
                                        invite=invite)

    def _event_invite_delete(self, shard, payload):
        invite = self.invites.get(payload['code'])
        if invite is not None:
            invite._delete()

        return events.InviteDeleteEvent(shard=shard, payload=payload,
                                        invite=invite)

    def _event_message_create(self, shard, payload):
        message = None
        channel = self.channels.get(payload['channel_id'])
        if channel is not None:
            message = channel.messages.upsert(payload)

        return events.MessageCreateEvent(shard=shard, payload=payload,
                                         channel=channel, message=message)

    def _event_message_update(self, shard, payload):
        message = None
        channel = self.channels.get(payload['channel_id'])
        if channel is not None:
            message = channel.messages.upsert(payload)

        return events.MessageUpdateEvent(shard=shard, payload=payload,
                                         channel=channel, message=message)

    def _event_message_delete(self, shard, payload):
        message = None
        channel = self.channels.get(payload['channel_id'])
        if channel is not None:
            message = channel.messages.get(payload['id'])
            if message is not None:
                message._delete()

        return events.MessageDeleteEvent(shard=shard, payload=payload,
                                         channel=channel, message=message)

    def _event_stage_instance_create(self, shard, payload):
        stage = self.stages.upsert(payload)
        return events.StageInstanceCreateEvent(shard=shard, payload=payload,
                                               stage=stage)

    def _event_stage_instance_update(self, shard, payload):
        stage = self.stages.upsert(payload)
        return events.StageInstanceUpdateEvent(shard=shard, payload=payload,
                                               stage=stage)

    def _event_state_instance_delete(self, shard, payload):
        stage = self.stages.upsert(payload)
        stage._delete()
        return events.StageInstanceCreateEvent(shard=shard, payload=payload,
                                               stage=stage)

    async def fetch_gateway(self):
        data = await rest.get_gateway.request(session=self.manager.rest)
        return data

    async def connect(self, *args, **kwargs):
        gateway = await self.fetch_gateway()

        intents = WebSocketIntents(guilds=True, guild_messages=True)

        shard = await self.sharder.create_connection(
            0, gateway['url'], intents=intents,
            token=self.manager.token)

        self.shards[0] = shard

        await self.sharder.work()

    def run_forever(self):
        self.manager.loop.create_task(self.connect())
        self.manager.run_forever()
