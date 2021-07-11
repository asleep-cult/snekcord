from ..utils import Snowflake

__all__ = []

WS_EVENTS = {}


def register(name):
    def wrapped(cls):
        __all__.append(cls.__name__)
        WS_EVENTS[name.lower()] = cls.execute
        return cls
    return wrapped


class BaseEvent:
    _fields_ = ('shard', 'payload')

    def __init__(self, **kwargs):
        for field in self._fields_:
            setattr(self, field, kwargs[field])

    def __init_subclass__(cls) -> None:
        for base in cls.__bases__:
            if issubclass(base, BaseEvent):
                cls._fields_ += base._fields_

    def __repr__(self):
        attrs = [
            (field, getattr(self, field))
            for field in self._fields_
            if field != 'payload'
        ]
        formatted = ', '.join(f'{name}={value}' for name, value in attrs)
        return f'<{self.__class__.__name__} {formatted}>'

    @classmethod
    async def execute(cls, client, shard, payload):
        raise NotImplementedError

    @property
    def partial(self):
        return False


@register('CHANNEL_CREATE')
class ChannelCreateEvent(BaseEvent):
    _fields_ = ('channel',)

    @classmethod
    async def execute(cls, client, shard, payload):
        channel = client.channels.upsert(payload)
        return cls(shard=shard, payload=payload, channel=channel)


@register('CHANNEL_UPDATE')
class ChannelUpdateEvent(BaseEvent):
    _fields_ = ('channel',)

    @classmethod
    async def execute(cls, client, shard, payload):
        channel = client.channels.upsert(payload)
        return cls(shard=shard, payload=payload, channel=channel)


@register('CHANNEL_DELETE')
class ChannelDeleteEvent(BaseEvent):
    _fields_ = ('channel',)

    @classmethod
    async def execute(cls, client, shard, payload):
        channel = client.channels.upsert(payload)
        channel._delete()
        return cls(shard=shard, payload=payload, channel=channel)


@register('CHANNEL_PINS_UPDATE')
class ChannelPinsUpdateEvent(BaseEvent):
    _fields_ = ('channel',)

    @classmethod
    async def execute(cls, client, shard, payload):
        channel = client.channels.get(Snowflake(payload['channel_id']))

        if channel is not None:
            channel.last_pin_timestamp = payload['last_pin_timestamp']

        return cls(shard=shard, payload=payload, channel=channel)

    @property
    def partial(self):
        return self.channel is None


@register('GUILD_RECEIVE')
class GuildReceiveEvent(BaseEvent):
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        await guild.sync(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register('GUILD_RECEIVE')
class GuildAvailableEvent(BaseEvent):
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        await guild.sync(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register('GUILD_JOIN')
class GuildJoinEvent(BaseEvent):
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        await guild.sync(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register('GUILD_UPDATE')
class GuildUpdateEvent(BaseEvent):
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        await guild.sync(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register('GUILD_UNAVAILABLE')
class GuildUnavailableEvent(BaseEvent):
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register('GUILD_DELETE')
class GuildDeleteEvent(BaseEvent):
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        guild._delete()
        return cls(shard=shard, payload=payload, guild=guild)


@register('GUILD_BAN_ADD')
class GuildBanAddEvent(BaseEvent):
    _fields_ = ('guild', 'ban')

    @classmethod
    async def execute(cls, client, shard, payload):
        ban = None
        guild = client.guilds.get(Snowflake(payload['guild_id']))

        if guild is not None:
            ban = guild.bans.upsert(payload)

        return cls(shard=shard, payload=payload, guild=guild, ban=ban)

    @property
    def partial(self):
        return self.guild is None


@register('GUILD_BAN_REMOVE')
class GuildBanRemoveEvent(BaseEvent):
    _fields_ = ('guild', 'ban')

    @classmethod
    async def execute(cls, client, shard, payload):
        ban = None
        guild = client.guilds.get(Snowflake(payload['guild_id']))

        if guild is not None:
            ban = guild.bans.upsert(payload)
            ban._delete()

        return cls(shard=shard, payload=payload, guild=guild, ban=ban)

    @property
    def partial(self):
        return self.guild is None


@register('GUILD_EMOJIS_UPDATE')
class GuildEmojisUpdateEvent(BaseEvent):
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.get(Snowflake(payload['guild_id']))

        if guild is not None:
            emojis = set()

            for emoji in payload['emojis']:
                emojis.add(guild.emojis.upsert(emoji).id)

            for emoji_id in set(guild.emojis.keys()) - emojis:
                del guild.emojis.mapping[emoji_id]

        return cls(shard=shard, payload=payload, guild=guild)

    @property
    def partial(self):
        return self.guild is None


@register('GUILD_INTEGRATIONS_UPDATE')
class GuildIntegrationsUpdateEvent(BaseEvent):
    _fields_ = ('guild',)


@register('GUILD_MEMBER_ADD')
class GuildMemberAddEvent(BaseEvent):
    _fields_ = ('guild', 'member')

    @classmethod
    async def execute(cls, client, shard, payload):
        member = None
        guild = client.guilds.get(Snowflake(payload['guild_id']))

        if guild is not None:
            member = guild.members.upsert(payload)

        return cls(shard=shard, payload=payload, guild=guild, member=member)

    @property
    def partial(self):
        return self.guild is None


@register('GUILD_MEMBER_UPDATE')
class GuildMemberUpdateEvent(BaseEvent):
    _fields_ = ('guild', 'member')

    @classmethod
    async def execute(cls, client, shard, payload):
        member = None
        guild = client.guilds.get(Snowflake(payload['guild_id']))

        if guild is not None:
            member = guild.members.upsert(payload)

        return cls(shard=shard, payload=payload, guild=guild, member=member)

    @property
    def partial(self):
        return self.guild is None


@register('GUILD_MEMBER_REMOVE')
class GuildMemberRemoveEvent(BaseEvent):
    _fields_ = ('user', 'guild', 'member')

    @classmethod
    async def execute(cls, client, shard, payload):
        member = None
        user = client.users.upsert(payload['user'])
        guild = client.guilds.get(Snowflake(payload['guild_id']))

        if guild is not None:
            member = guild.members.get(user.id)

            if member is not None:
                member._delete()

        return cls(shard=shard, payload=payload, user=user, guild=guild, member=member)

    @property
    def partial(self):
        return self.guild is None or self.member is None


@register('GUILD_ROLE_CREATE')
class GuildRoleCreateEvent(BaseEvent):
    _fields_ = ('guild', 'role')

    @classmethod
    async def execute(cls, client, shard, payload):
        role = None
        guild = client.guilds.get(Snowflake(payload['guild_id']))

        if guild is not None:
            role = guild.roles.upsert(payload['role'])

        return cls(shard=shard, payload=payload, guild=guild, role=role)

    @property
    def partial(self):
        return self.guild is None


@register('GUILD_ROLE_UPDATE')
class GuildRoleUpdateEvent(BaseEvent):
    _fields_ = ('guild', 'role')

    @classmethod
    async def execute(cls, client, shard, payload):
        role = None
        guild = client.guilds.get(Snowflake(payload['guild_id']))

        if guild is not None:
            role = guild.roles.upsert(payload['role'])

        return cls(shard=shard, payload=payload, guild=guild, role=role)

    @property
    def pertial(self):
        return self.guild is None


@register('GUILD_ROLE_DELETE')
class GuildRoleDeleteEvent(BaseEvent):
    _fields_ = ('guild', 'role')

    @classmethod
    async def execute(cls, client, shard, payload):
        role = None
        guild = client.guilds.get(Snowflake(payload['guild_id']))

        if guild is not None:
            role = guild.roles.get(Snowflake(payload['role_id']))

            if role is not None:
                role._delete()

        return cls(shard=shard, payload=payload, guild=guild, role=role)

    @property
    def partial(self):
        return self.guild is None or self.role is None


@register('INTEGRATION_CREATE')
class IntegrationCreateEvent(BaseEvent):
    pass


@register('INTEGRATION_UPDATE')
class IntegrationUpdateEvent(BaseEvent):
    pass


@register('INTEGRATION_DELETE')
class IntegrationDeleteEvent(BaseEvent):
    pass


@register('INVITE_CREATE')
class InviteCreateEvent(BaseEvent):
    _fields_ = ('invite',)

    @classmethod
    async def execute(cls, client, shard, payload):
        invite = client.invites.upsert(payload)
        return cls(shard=shard, payload=payload, invite=invite)


@register('INVITE_DELETE')
class InviteDeleteEvent(BaseEvent):
    _fields_ = ('invite',)

    @classmethod
    async def execute(cls, client, shard, payload):
        invite = client.invites.get(payload['code'])

        if invite is not None:
            invite._delete()

        return cls(shard=shard, payload=payload, invite=invite)

    @property
    def partial(self):
        return self.invite is None


@register('MESSAGE_CREATE')
class MessageCreateEvent(BaseEvent):
    _fields_ = ('channel', 'message')

    @classmethod
    async def execute(cls, client, shard, payload):
        message = None
        channel = client.channels.get(Snowflake(payload['channel_id']))

        if channel is not None:
            message = channel.messages.upsert(payload)
            channel._json_data_['last_message_id'] = message.id

        return cls(shard=shard, payload=payload, channel=channel, message=message)

    @property
    def partial(self):
        return self.channel is None


@register('MESSAGE_UPDATE')
class MessageUpdateEvent(BaseEvent):
    _fields_ = ('channel', 'message')

    @classmethod
    async def execute(cls, client, shard, payload):
        message = None
        channel = client.channels.get(Snowflake(payload['channel_id']))

        if channel is not None:
            message = channel.messages.upsert(payload)

        return cls(shard=shard, payload=payload, channel=channel, message=message)

    @property
    def partial(self):
        return self.channel is None


@register('MESSAGE_DELETE')
class MessageDeleteEvent(BaseEvent):
    _fields_ = ('channel', 'message')

    @classmethod
    async def execute(cls, client, shard, payload):
        message = None
        channel = client.channels.get(Snowflake(payload['channel_id']))

        if channel is not None:
            message = channel.messages.get(Snowflake(payload['id']))

            if message is not None:
                message._delete()

        return cls(shard=shard, payload=payload, channel=channel, message=message)

    @property
    def partial(self):
        return self.channel is None or self.message is None


@register('MESSAGE_DELETE_BULK')
class MessageDeleteBulkEvent(BaseEvent):
    _fields_ = ('channel', 'messages')

    @classmethod
    async def execute(cls, client, shard, payload):
        messages = []
        channel = client.channels.get(Snowflake(payload['channel_id']))

        if channel is not None:
            for message in payload['id']:
                message = channel.messages.get(message)

                if message is not None:
                    messages.append(message)

        return cls(shard=shard, payload=payload, channel=channel, messages=messages)

    @property
    def partial(self):
        return self.channel is None


@register('MESSAGE_REACTION_ADD')
class MessageReactionAddEvent(BaseEvent):
    _fields_ = ('channel', 'message', 'reactions', 'user')

    @classmethod
    async def execute(cls, client, shard, payload):
        message = None
        reactions = None
        channel = client.channels.get(Snowflake(payload['channel_id']))
        user = client.users.get(payload['user_id'])

        if channel is not None:
            message = channel.messages.get(Snowflake(payload['message_id']))
            if message is not None:
                reactions = message.reactions.upsert(payload)

        return cls(
            shard=shard, payload=payload, channel=channel, message=message,
            reactions=reactions, user=user
        )

    @property
    def partial(self):
        return self.channel is None or self.message is None or self.user is None


@register('STAGE_INSTANCE_CREATE')
class StageInstanceCreateEvent(BaseEvent):
    _fields_ = ('stage',)

    @classmethod
    async def execute(cls, client, shard, payload):
        stage = client.stages.upsert(payload)
        return cls(shard=shard, payload=payload, stage=stage)


@register('STAGE_INSTANCE_UPDATE')
class StageInstanceUpdateEvent(BaseEvent):
    _fields_ = ('stage',)

    @classmethod
    async def execute(cls, client, shard, payload):
        stage = client.stages.upsert(payload)
        return cls(shard=shard, payload=payload, stage=stage)


@register('STAGE_INSTANCE_DELETE')
class StageInstanceDeleteEvent(BaseEvent):
    _fields_ = ('stage',)

    @classmethod
    async def execute(cls, client, shard, payload):
        stage = client.stages.upsert(payload)
        stage._delete()
        return cls(shard=shard, payload=payload, stage=stage)
