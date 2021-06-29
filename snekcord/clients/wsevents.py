__all__ = []

WS_EVENTS = {}


def register(cls):
    __all__.append(cls.__name__)
    WS_EVENTS[cls.__event_name__.lower()] = cls.execute
    return cls


class BaseEvent:
    __fields__ = ('shard', 'payload')

    def __init__(self, **kwargs):
        for field in self.__fields__:
            setattr(self, field, kwargs[field])

    def __init_subclass__(cls) -> None:
        for base in cls.__bases__:
            if issubclass(base, BaseEvent):
                cls.__fields__ += base.__fields__

    def __repr__(self):
        attrs = [
            (field, getattr(self, field))
            for field in self.__fields__
            if field != 'payload'
        ]
        formatted = ', '.join(f'{name}={value}' for name, value in attrs)
        return f'{self.__class__.__name__}({formatted})'

    @classmethod
    async def execute(cls, client, shard, payload):
        raise NotImplementedError


@register
class ChannelCreateEvent(BaseEvent):
    __event_name__ = 'CHANNEL_CREATE'
    __fields__ = ('channel',)

    @classmethod
    async def execute(cls, client, shard, payload):
        channel = client.channels.upsert(payload)
        return cls(shard=shard, payload=payload, channel=channel)


@register
class ChannelUpdateEvent(BaseEvent):
    __event_name__ = 'CHANNEL_UPDATE'
    __fields__ = ('channel',)

    @classmethod
    async def execute(cls, client, shard, payload):
        channel = client.channels.upsert(payload)
        return cls(shard=shard, payload=payload, channel=channel)


@register
class ChannelDeleteEvent(BaseEvent):
    __event_name__ = 'CHANNEL_DELETE'
    __fields__ = ('channel',)

    @classmethod
    async def execute(cls, client, shard, payload):
        channel = client.channels.upsert(payload)
        channel._delete()
        return cls(shard=shard, payload=payload, channel=channel)


@register
class ChannelPinsUpdateEvent(BaseEvent):
    __event_name__ = 'CHANNEL_PINS_UPDATE'
    __fields__ = ('channel',)

    @classmethod
    async def execute(cls, client, shard, payload):
        channel = client.channels.get(
            payload['channel_id'])

        if channel is not None:
            channel.last_pin_timestamp = payload['last_pin_timestamp']

        return cls(shard=shard, payload=payload, channel=channel)


@register
class GuildReceiveEvent(BaseEvent):
    __event_name__ = 'GUILD_RECEIVE'
    __fields__ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        await guild.sync(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildAvailableEvent(BaseEvent):
    __event_name__ = 'GUILD_AVAILABLE'
    __fields__ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        await guild.sync(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildJoinEvent(BaseEvent):
    __event_name__ = 'GUILD_JOIN'
    __fields__ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        await guild.sync(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildUpdateEvent(BaseEvent):
    __event_name__ = 'GUILD_UPDATE'
    __fields__ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        await guild.sync(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildUnavailableEvent(BaseEvent):
    __event_name__ = 'GUILD_UNAVAILABLE'
    __fields__ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildDeleteEvent(BaseEvent):
    __event_name__ = 'GUILD_DELETE'
    __fields__ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        guild._delete()
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildBanAddEvent(BaseEvent):
    __event_name__ = 'GUILD_BAN_ADD'
    __fields__ = ('guild', 'ban')

    @classmethod
    async def execute(cls, client, shard, payload):
        ban = None
        guild = client.guilds.get(payload['guild_id'])

        if guild is not None:
            ban = guild.bans.upsert(payload)

        return cls(shard=shard, payload=payload, guild=guild, ban=ban)


@register
class GuildBanRemoveEvent(BaseEvent):
    __event_name__ = 'GUILD_BAN_REMOVE'
    __fields__ = ('guild', 'ban')

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
    __event_name__ = 'GUILD_EMOJIS_UPDATE'
    __fields__ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.get(payload['guild_id'])

        if guild is not None:
            guild.emojis.upsert_replace(payload['emojis'])

        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildIntegrationsUpdateEvent(BaseEvent):
    __event_name__ = 'GUILD_INTEGRATIONS_UPDATE'
    __fields__ = ('guild',)


@register
class GuildMemberAddEvent(BaseEvent):
    __event_name__ = 'GUILD_MEMBER_ADD'
    __fields__ = ('guild', 'member')

    @classmethod
    async def execute(cls, client, shard, payload):
        member = None
        guild = client.guilds.get(payload['guild_id'])

        if guild is not None:
            member = guild.members.upsert(payload)

        return cls(shard=shard, payload=payload, guild=guild, member=member)


@register
class GuildMemberUpdateEvent(BaseEvent):
    __event_name__ = 'GUILD_MEMBER_UPDATE'
    __fields__ = ('guild', 'member')

    @classmethod
    async def execute(cls, client, shard, payload):
        member = None
        guild = client.guilds.get(payload['guild_id'])

        if guild is not None:
            member = guild.members.upsert(payload)

        return cls(shard=shard, payload=payload, guild=guild, member=member)


@register
class GuildMemberRemoveEvent(BaseEvent):
    __event_name__ = 'GUILD_MEMBER_REMOVE'
    __fields__ = ('user', 'guild', 'member')

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
    __event_name__ = 'GUILD_ROLE_CREATE'
    __fields__ = ('guild', 'role')

    @classmethod
    async def execute(cls, client, shard, payload):
        role = None
        guild = client.guilds.get(payload['guild_id'])

        if guild is not None:
            role = guild.roles.upsert(payload['role'])

        return cls(shard=shard, payload=payload, guild=guild, role=role)


@register
class GuildRoleUpdateEvent(BaseEvent):
    __event_name__ = 'GUILD_ROLE_UPDATE'
    __fields__ = ('guild', 'role')

    @classmethod
    async def execute(cls, client, shard, payload):
        role = None
        guild = client.guilds.get(payload['guild_id'])

        if guild is not None:
            role = guild.roles.upsert(payload['role'])

        return cls(shard=shard, payload=payload, guild=guild, role=role)


@register
class GuildRoleDeleteEvent(BaseEvent):
    __event_name__ = 'GUILD_ROLE_DELETE'
    __fields__ = ('guild', 'role')

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
    __event_name__ = 'INTEGRATION_CREATE'


@register
class IntegrationUpdateEvent(BaseEvent):
    __event_name__ = 'INTEGRATION_UPDATE'


@register
class IntegrationDeleteEvent(BaseEvent):
    __event_name__ = 'INTEGRATION_DELETE'


@register
class InviteCreateEvent(BaseEvent):
    __event_name__ = 'INVITE_CREATE'
    __fields__ = ('invite',)

    @classmethod
    async def execute(cls, client, shard, payload):
        invite = client.invites.upsert(payload)
        return cls(shard=shard, payload=payload, invite=invite)


@register
class InviteDeleteEvent(BaseEvent):
    __event_name__ = 'INVITE_DELETE'
    __fields__ = ('invite',)

    @classmethod
    async def execute(cls, client, shard, payload):
        invite = client.invites.get(payload['code'])

        if invite is not None:
            invite._delete()

        return cls(shard=shard, payload=payload, invite=invite)


@register
class MessageCreateEvent(BaseEvent):
    __event_name__ = 'MESSAGE_CREATE'
    __fields__ = ('channel', 'message')

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
    __event_name__ = 'MESSAGE_UPDATE'
    __fields__ = ('channel', 'message')

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
    __event_name__ = 'MESSAGE_DELETE'
    __fields__ = ('channel', 'message')

    @classmethod
    async def execute(cls, client, shard, payload):
        message = None
        channel = client.channels.get(
            payload['channel_id']
        )

        if channel is not None:
            message = channel.messages.get(payload['id'])
            if message is not None:
                message._delete()

        return cls(shard=shard, payload=payload, channel=channel,
                   message=message)


@register
class MessageDeleteBulkEvent(BaseEvent):
    __event_name__ = 'MESSAGE_DELETE_BULK'
    __fields__ = ('channel', 'messages')

    @classmethod
    async def execute(cls, client, shard, payload):
        messages = []
        channel = client.channels.get(payload['channel_id'])

        if channel is not None:
            for message in payload['ids']:
                message = channel.messages.get(message)
                if message is not None:
                    messages.append(message)
                    message._delete()

        return cls(shard=shard, payload=payload, channel=channel,
                   messages=messages)


@register
class MessageReactionAddEvent(BaseEvent):
    __event_name__ = 'MESSAGE_REACTION_ADD'
    __fields__ = ('channel', 'message', 'reactions', 'user')

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
    __event_name__ = 'STAGE_INSTANCE_CREATE'
    __fields__ = ('stage',)

    @classmethod
    async def execute(cls, client, shard, payload):
        stage = client.stages.upsert(payload)
        return cls(shard=shard, payload=payload, stage=stage)


@register
class StageInstanceUpdateEvent(BaseEvent):
    __event_name__ = 'STAGE_INSTANCE_UPDATE'
    __fields__ = ('stage',)

    @classmethod
    async def execute(cls, client, shard, payload):
        stage = client.stages.upsert(payload)
        return cls(shard=shard, payload=payload, stage=stage)


@register
class StageInstanceDeleteEvent(BaseEvent):
    __event_name__ = 'STAGE_INSTANCE_DELETE'
    __fields__ = ('stage',)

    @classmethod
    async def execute(cls, client, shard, payload):
        stage = client.stages.upsert(payload)
        stage._delete()
        return cls(shard=shard, payload=payload, stage=stage)
