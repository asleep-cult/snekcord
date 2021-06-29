__all__ = []

WS_EVENTS = {}


def register(cls):
    __all__.append(cls.__name__)
    WS_EVENTS[cls._event_name_.lower()] = cls.execute
    return cls


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


@register
class ChannelCreateEvent(BaseEvent):
    _event_name_ = 'CHANNEL_CREATE'
    _fields_ = ('channel',)

    @classmethod
    async def execute(cls, client, shard, payload):
        channel = client.channels.upsert(payload)
        return cls(shard=shard, payload=payload, channel=channel)


@register
class ChannelUpdateEvent(BaseEvent):
    _event_name_ = 'CHANNEL_UPDATE'
    _fields_ = ('channel',)

    @classmethod
    async def execute(cls, client, shard, payload):
        channel = client.channels.upsert(payload)
        return cls(shard=shard, payload=payload, channel=channel)


@register
class ChannelDeleteEvent(BaseEvent):
    _event_name_ = 'CHANNEL_DELETE'
    _fields_ = ('channel',)

    @classmethod
    async def execute(cls, client, shard, payload):
        channel = client.channels.upsert(payload)
        channel._delete()
        return cls(shard=shard, payload=payload, channel=channel)


@register
class ChannelPinsUpdateEvent(BaseEvent):
    _event_name_ = 'CHANNEL_PINS_UPDATE'
    _fields_ = ('channel',)

    @classmethod
    async def execute(cls, client, shard, payload):
        channel = client.channels.get(
            payload['channel_id'])

        if channel is not None:
            channel.last_pin_timestamp = payload['last_pin_timestamp']

        return cls(shard=shard, payload=payload, channel=channel)


@register
class GuildReceiveEvent(BaseEvent):
    _event_name_ = 'GUILD_RECEIVE'
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        await guild.sync(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildAvailableEvent(BaseEvent):
    _event_name_ = 'GUILD_AVAILABLE'
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        await guild.sync(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildJoinEvent(BaseEvent):
    _event_name_ = 'GUILD_JOIN'
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        await guild.sync(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildUpdateEvent(BaseEvent):
    _event_name_ = 'GUILD_UPDATE'
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        await guild.sync(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildUnavailableEvent(BaseEvent):
    _event_name_ = 'GUILD_UNAVAILABLE'
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildDeleteEvent(BaseEvent):
    _event_name_ = 'GUILD_DELETE'
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        guild._delete()
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildBanAddEvent(BaseEvent):
    _event_name_ = 'GUILD_BAN_ADD'
    _fields_ = ('guild', 'ban')

    @classmethod
    async def execute(cls, client, shard, payload):
        ban = None
        guild = client.guilds.get(payload['guild_id'])

        if guild is not None:
            ban = guild.bans.upsert(payload)

        return cls(shard=shard, payload=payload, guild=guild, ban=ban)


@register
class GuildBanRemoveEvent(BaseEvent):
    _event_name_ = 'GUILD_BAN_REMOVE'
    _fields_ = ('guild', 'ban')

    @classmethod
    async def execute(cls, client, shard, payload):
        ban = None
        guild = client.guilds.get(payload['guild_id'])

        if guild is not None:
            ban = guild.bans.upsert(payload)
            ban._delete()

        return cls(shard=shard, payload=payload, guild=guild, ban=ban)


@register
class GuildEmojisUpdateEvent(BaseEvent):
    _event_name_ = 'GUILD_EMOJIS_UPDATE'
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.get(payload['guild_id'])

        if guild is not None:
            guild.emojis.upsert_replace(payload['emojis'])

        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildIntegrationsUpdateEvent(BaseEvent):
    _event_name_ = 'GUILD_INTEGRATIONS_UPDATE'
    _fields_ = ('guild',)


@register
class GuildMemberAddEvent(BaseEvent):
    _event_name_ = 'GUILD_MEMBER_ADD'
    _fields_ = ('guild', 'member')

    @classmethod
    async def execute(cls, client, shard, payload):
        member = None
        guild = client.guilds.get(payload['guild_id'])

        if guild is not None:
            member = guild.members.upsert(payload)

        return cls(shard=shard, payload=payload, guild=guild, member=member)


@register
class GuildMemberUpdateEvent(BaseEvent):
    _event_name_ = 'GUILD_MEMBER_UPDATE'
    _fields_ = ('guild', 'member')

    @classmethod
    async def execute(cls, client, shard, payload):
        member = None
        guild = client.guilds.get(payload['guild_id'])

        if guild is not None:
            member = guild.members.upsert(payload)

        return cls(shard=shard, payload=payload, guild=guild, member=member)


@register
class GuildMemberRemoveEvent(BaseEvent):
    _event_name_ = 'GUILD_MEMBER_REMOVE'
    _fields_ = ('user', 'guild', 'member')

    @classmethod
    async def execute(cls, client, shard, payload):
        member = None
        user = client.users.upsert(payload['user'])
        guild = client.guilds.get(payload['guild_id'])

        if guild is not None:
            member = guild.members.get(user.id)
            if member is not None:
                member._delete()

        return cls(shard=shard, payload=payload, user=user, guild=guild,
                   member=member)


@register
class GuildRoleCreateEvent(BaseEvent):
    _event_name_ = 'GUILD_ROLE_CREATE'
    _fields_ = ('guild', 'role')

    @classmethod
    async def execute(cls, client, shard, payload):
        role = None
        guild = client.guilds.get(payload['guild_id'])

        if guild is not None:
            role = guild.roles.upsert(payload['role'])

        return cls(shard=shard, payload=payload, guild=guild, role=role)


@register
class GuildRoleUpdateEvent(BaseEvent):
    _event_name_ = 'GUILD_ROLE_UPDATE'
    _fields_ = ('guild', 'role')

    @classmethod
    async def execute(cls, client, shard, payload):
        role = None
        guild = client.guilds.get(payload['guild_id'])

        if guild is not None:
            role = guild.roles.upsert(payload['role'])

        return cls(shard=shard, payload=payload, guild=guild, role=role)


@register
class GuildRoleDeleteEvent(BaseEvent):
    _event_name_ = 'GUILD_ROLE_DELETE'
    _fields_ = ('guild', 'role')

    @classmethod
    async def execute(cls, client, shard, payload):
        role = None
        guild = client.guilds.get(payload['guild_id'])

        if guild is not None:
            role = guild.roles.get(payload['role_id'])
            if role is not None:
                role._delete()

        return cls(shard=shard, payload=payload, guild=guild, role=role)


@register
class IntegrationCreateEvent(BaseEvent):
    _event_name_ = 'INTEGRATION_CREATE'


@register
class IntegrationUpdateEvent(BaseEvent):
    _event_name_ = 'INTEGRATION_UPDATE'


@register
class IntegrationDeleteEvent(BaseEvent):
    _event_name_ = 'INTEGRATION_DELETE'


@register
class InviteCreateEvent(BaseEvent):
    _event_name_ = 'INVITE_CREATE'
    _fields_ = ('invite',)

    @classmethod
    async def execute(cls, client, shard, payload):
        invite = client.invites.upsert(payload)
        return cls(shard=shard, payload=payload, invite=invite)


@register
class InviteDeleteEvent(BaseEvent):
    _event_name_ = 'INVITE_DELETE'
    _fields_ = ('invite',)

    @classmethod
    async def execute(cls, client, shard, payload):
        invite = client.invites.get(payload['code'])

        if invite is not None:
            invite._delete()

        return cls(shard=shard, payload=payload, invite=invite)


@register
class MessageCreateEvent(BaseEvent):
    _event_name_ = 'MESSAGE_CREATE'
    _fields_ = ('channel', 'message')

    @classmethod
    async def execute(cls, client, shard, payload):
        message = None
        channel = client.channels.get(payload['channel_id'])

        if channel is not None:
            message = channel.messages.upsert(payload)

        return cls(shard=shard, payload=payload, channel=channel,
                   message=message)


@register
class MessageUpdateEvent(BaseEvent):
    _event_name_ = 'MESSAGE_UPDATE'
    _fields_ = ('channel', 'message')

    @classmethod
    async def execute(cls, client, shard, payload):
        message = None
        channel = client.channels.get(payload['channel_id'])

        if channel is not None:
            message = channel.messages.upsert(payload)

        return cls(shard=shard, payload=payload, channel=channel,
                   message=message)


@register
class MessageDeleteEvent(BaseEvent):
    _event_name_ = 'MESSAGE_DELETE'
    _fields_ = ('channel', 'message')

    @classmethod
    async def execute(cls, client, shard, payload):
        message = None
        channel = client.channels.get(payload['channel_id'])

        if channel is not None:
            message = channel.messages.get(payload['id'])
            if message is not None:
                message._delete()

        return cls(shard=shard, payload=payload, channel=channel,
                   message=message)


@register
class MessageDeleteBulkEvent(BaseEvent):
    _event_name_ = 'MESSAGE_DELETE_BULK'
    _fields_ = ('channel', 'messages')

    @classmethod
    async def execute(cls, client, shard, payload):
        messages = []
        channel = client.channels.get(payload['channel_id'])

        if channel is not None:
            for message in payload['id']:
                message = channel.messages.get(message)
                if message is not None:
                    messages.append(message)

        return cls(shard=shard, payload=payload, channel=channel,
                   messages=messages)


@register
class MessageReactionAddEvent(BaseEvent):
    _event_name_ = 'MESSAGE_REACTION_ADD'
    _fields_ = ('channel', 'message', 'reactions', 'user')

    @classmethod
    async def execute(cls, client, shard, payload):
        message = None
        reactions = None
        channel = client.channels.get(payload['channel_id'])
        user = client.users.get(payload['user_id'])

        if channel is not None:
            message = channel.messages.get(payload['message_id'])
            if message is not None:
                reactions = message.reactions.upsert(payload)

        return cls(shard=shard, payload=payload, channel=channel,
                   message=message, reactions=reactions, user=user)


@register
class StageInstanceCreateEvent(BaseEvent):
    _event_name_ = 'STAGE_INSTANCE_CREATE'
    _fields_ = ('stage',)

    @classmethod
    async def execute(cls, client, shard, payload):
        stage = client.stages.upsert(payload)
        return cls(shard=shard, payload=payload, stage=stage)


@register
class StageInstanceUpdateEvent(BaseEvent):
    _event_name_ = 'STAGE_INSTANCE_UPDATE'
    _fields_ = ('stage',)

    @classmethod
    async def execute(cls, client, shard, payload):
        stage = client.stages.upsert(payload)
        return cls(shard=shard, payload=payload, stage=stage)


@register
class StageInstanceDeleteEvent(BaseEvent):
    _event_name_ = 'STAGE_INSTANCE_DELETE'
    _fields_ = ('stage',)

    @classmethod
    async def execute(cls, client, shard, payload):
        stage = client.stages.upsert(payload)
        stage._delete()
        return cls(shard=shard, payload=payload, stage=stage)
