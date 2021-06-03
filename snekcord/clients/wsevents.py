from collections import namedtuple

EVENTS = {}


def register(cls):
    EVENTS[cls.__event_name__.lower()] = cls.execute
    return cls


class BaseEvent:
    __fields__ = ('shard', 'payload')

    def __init__(self, **kwargs):
        for field in self.__fields__:
            setattr(self, field, kwargs[field])

    def __repr__(self):
        attrs = [
            (field, getattr(self, field))
            for field in self.__fields__
            if field != 'payload'
        ]
        formatted = ', '.join(f'{name}={value}' for name, value in attrs)
        return f'{self.__class__.__name__}({formatted})'

    @classmethod
    async def execute(cls, manager, shard, payload):
        raise NotImplementedError


@register
class ChannelCreateEvent(BaseEvent):
    __event_name__ = 'CHANNEL_CREATE'
    __fields__ = (*BaseEvent.__fields__, 'channel')

    @classmethod
    async def execute(cls, manager, shard, payload):
        channel = manager.channels.upsert(payload)
        return cls(shard=shard, payload=payload, channel=channel)


@register
class ChannelUpdateEvent(BaseEvent):
    __event_name__ = 'CHANNEL_UPDATE'
    __fields__ = (*BaseEvent.__fields__, 'channel')

    @classmethod
    async def execute(cls, manager, shard, payload):
        channel = manager.channels.upsert(payload)
        return cls(shard=shard, payload=payload, channel=channel)


@register
class ChannelDeleteEvent(BaseEvent):
    __event_name__ = 'CHANNEL_DELETE'
    __fields__ = (*BaseEvent.__fields__, 'channel')

    @classmethod
    async def execute(cls, manager, shard, payload):
        channel = manager.channels.upsert(payload)
        channel._delete()
        return cls(shard=shard, payload=payload, channel=channel)


@register
class ChannelPinsUpdateEvent(BaseEvent):
    __event_name__ = 'CHANNEL_PINS_UPDATE'
    __fields__ = (*BaseEvent.__fields__, 'channel')

    @classmethod
    async def execute(cls, manager, shard, payload):
        channel = manager.channels.get(payload['channel_id'])
        if channel is not None:
            channel.last_pin_timestamp = payload['last_pin_timestamp']
        return cls(shard=shard, payload=payload, channel=channel)


@register
class GuildReceiveEvent(BaseEvent):
    __event_name__ = 'GUILD_RECEIVE'
    __fields__ = (*BaseEvent.__fields__, 'guild')

    @classmethod
    async def execute(cls, manager, shard, payload):
        guild = manager.guilds.upsert(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildAvailableEvent(BaseEvent):
    __event_name__ = 'GUILD_AVAILABLE'
    __fields__ = (*BaseEvent.__fields__, 'guild')

    @classmethod
    async def execute(cls, manager, shard, payload):
        guild = manager.guilds.upsert(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildJoinEvent(BaseEvent):
    __event_name__ = 'GUILD_JOIN'
    __fields__ = (*BaseEvent.__fields__, 'guild')

    @classmethod
    async def execute(cls, manager, shard, payload):
        guild = manager.guilds.upsert(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildUpdateEvent(BaseEvent):
    __event_name__ = 'GUILD_UPDATE'
    __fields__ = (*BaseEvent.__fields__, 'guild')

    @classmethod
    async def execute(cls, manager, shard, payload):
        guild = manager.guilds.upsert(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildUnavailableEvent(BaseEvent):
    __event_name__ = 'GUILD_UNAVAILABLE'
    __fields__ = (*BaseEvent.__fields__, 'guild')

    @classmethod
    async def execute(cls, manager, shard, payload):
        guild = manager.guilds.upsert(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildDeleteEvent(BaseEvent):
    __event_name__ = 'GUILD_DELETE'
    __fields__ = (*BaseEvent.__fields__, 'guild')

    @classmethod
    async def execute(cls, manager, shard, payload):
        guild = manager.guilds.upsert(payload)
        guild._delete()
        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildBanAddEvent(BaseEvent):
    __event_name__ = 'GUILD_BAN_ADD'
    __fields__ = (*BaseEvent.__fields__, 'guild', 'ban')

    @classmethod
    async def execute(cls, manager, shard, payload):
        ban = None
        guild = manager.guilds.get(payload['guild_id'])

        if guild is not None:
            ban = guild.bans.upsert(payload)

        return cls(shard=shard, payload=payload, guild=guild, ban=ban)


@register
class GuildBanRemoveEvent(BaseEvent):
    __event_name__ = 'GUILD_BAN_REMOVE'
    __fields__ = (*BaseEvent.__fields__, 'guild', 'ban')

    @classmethod
    async def execute(cls, manager, shard, payload):
        ban = None
        guild = manager.guilds.get(payload['guild_id'])

        if guild is not None:
            ban = guild.bans.upsert(payload)
            ban._delete()

        return cls(shard=shard, payload=payload, guild=guild, ban=ban)


@register
class GuildEmojisUpdateEvent(BaseEvent):
    __event_name__ = 'GUILD_EMOJIS_UPDATE'
    __fields__ = (*BaseEvent.__fields__, 'guild')

    @classmethod
    async def execute(cls, manager, shard, payload):
        guild = manager.guilds.get(payload['guild_id'])

        if guild is not None:
            guild._update_emojis(payload['emojis'])

        return cls(shard=shard, payload=payload, guild=guild)


@register
class GuildIntegrationsUpdateEvent(BaseEvent):
    __event_name__ = 'GUILD_INTEGRATIONS_UPDATE'
    __fields__ = (*BaseEvent.__fields__, 'guild')

    @classmethod
    async def execute(cls, manager, shard, payload):
        pass


@register
class GuildMemberAddEvent(BaseEvent):
    __event_name__ = 'GUILD_MEMBER_ADD'
    __fields__ = (*BaseEvent.__fields__, 'guild', 'member')

    @classmethod
    async def execute(cls, manager, shard, payload):
        member = None
        guild = manager.guilds.get(payload['guild_id'])

        if guild is not None:
            member = guild.members.upsert(payload)

        return cls(shard=shard, payload=payload, member=member)


@register
class GuildMemberUpdateEvent(BaseEvent):
    __event_name__ = 'GUILD_MEMBER_UPDATE'
    __fields__ = (*BaseEvent.__fields__, 'guild', 'member')

    @classmethod
    async def execute(cls, manager, shard, payload):
        member = None
        guild = manager.guilds.get(payload['guild_id'])

        if guild is not None:
            member = guild.members.upsert(payload)

        return cls(shard=shard, payload=payload, member=member)


@register
class GuildMemberRemoveEvent(BaseEvent):
    __event_name__ = 'GUILD_MEMBER_REMOVE'
    __fields__ = (*BaseEvent.__fields__, 'user', 'guild', 'member')

    @classmethod
    async def execute(cls, manager, shard, payload):
        member = None
        user = manager.users.upsert(payload['user'])
        guild = manager.guilds.get(payload['guild_id'])

        if guild is not None:
            member = guild.members.get(user.id)
            if member is not None:
                member._delete()

        return cls(shard=shard, payload=payload, user=user, guild=guild,
                   member=member)


@register
class GuildRoleCreateEvent(BaseEvent):
    __event_name__ = 'GUILD_ROLE_CREATE'
    __fields__ = (*BaseEvent.__fields__, 'guild', 'role')

    @classmethod
    async def execute(cls, manager, shard, payload):
        role = None
        guild = manager.guilds.get(payload['guild_id'])

        if guild is not None:
            role = guild.roles.upsert(payload)

        return cls(shard=shard, payload=payload, guild=guild, role=role)


@register
class GuildRoleUpdateEvent(BaseEvent):
    __event_name__ = 'GUILD_ROLE_UPDATE'
    __fields__ = (*BaseEvent.__fields__, 'guild', 'role')

    @classmethod
    async def execute(cls, manager, shard, payload):
        role = None
        guild = manager.guilds.get(payload['guild_id'])

        if guild is not None:
            role = guild.roles.upsert(payload)

        return cls(shard=shard, payload=payload, guild=guild, role=role)


@register
class GuildRoleDeleteEvent(BaseEvent):
    __event_name__ = 'GUILD_ROLE_DELETE'
    __fields__ = (*BaseEvent.__fields__, 'guild', 'role')

    @classmethod
    async def execute(cls, manager, shard, payload):
        role = None
        guild = manager.guilds.get(payload['guild_id'])

        if guild is not None:
            role = guild.roles.upsert(payload)
            role._delete()

        return cls(shard=shard, payload=payload, guild=guild, role=role)


@register
class IntegrationCreateEvent(BaseEvent):
    __event_name__ = 'INTEGRATION_CREATE'

    @classmethod
    async def execute(cls, manager, shard, payload):
        pass


@register
class IntegrationUpdateEvent(BaseEvent):
    __event_name__ = 'INTEGRATION_UPDATE'

    @classmethod
    async def execute(cls, manager, shard, payload):
        pass


@register
class IntegrationDeleteEvent(BaseEvent):
    __event_name__ = 'INTEGRATION_DELETE'

    @classmethod
    async def execute(cls, manager, shard, payload):
        pass


@register
class InviteCreateEvent(BaseEvent):
    __event_name__ = 'INVITE_CREATE'
    __fields__ = (*BaseEvent.__fields__, 'invite')

    @classmethod
    async def execute(cls, manager, shard, payload):
        invite = manager.invites.get(payload['code'])
        return cls(shard=shard, payload=payload, invite=invite)


@register
class InviteDeleteEvent(BaseEvent):
    __event_name__ = 'INVITE_DELETE'
    __fields__ = (*BaseEvent.__fields__, 'invite')

    @classmethod
    async def execute(cls, manager, shard, payload):
        invite = manager.invites.get(payload['code'])

        if invite is not None:
            invite._delete()

        return cls(shard=shard, payload=payload, invite=invite)


@register
class MessageCreateEvent(BaseEvent):
    __event_name__ = 'MESSAGE_CREATE'
    __fields__ = (*BaseEvent.__fields__, 'channel', 'message')

    @classmethod
    async def execute(cls, manager, shard, payload):
        message = None
        channel = manager.channels.get(payload['channel_id'])

        if channel is not None:
            message = channel.messages.upsert(payload)

        return cls(shard=shard, payload=payload, channel=channel,
                   message=message)


@register
class MessageUpdateEvent(BaseEvent):
    __event_name__ = 'MESSAGE_UPDATE'
    __fields__ = (*BaseEvent.__fields__, 'channel', 'message')

    @classmethod
    async def execute(cls, manager, shard, payload):
        message = None
        channel = manager.channels.get(payload['channel_id'])

        if channel is not None:
            message = channel.messages.upsert(payload)

        return cls(shard=shard, payload=payload, channel=channel,
                   message=message)


@register
class MessageDeleteEvent(BaseEvent):
    __event_name__ = 'MESSAGE_DELETE'
    __fields__ = (*BaseEvent.__fields__, 'channel', 'message')

    @classmethod
    async def execute(cls, manager, shard, payload):
        message = None
        channel = manager.channels.get(payload['channel_id'])

        if channel is not None:
            message = channel.messages.get(payload['id'])
            if message is not None:
                message._delete()

        return cls(shard=shard, payload=payload, channel=channel,
                   message=message)


@register
class StageInstanceCreateEvent(BaseEvent):
    __event_name__ = 'STAGE_INSTANCE_CREATE'
    __fields__ = (*BaseEvent.__fields__, 'stage')

    @classmethod
    async def execute(cls, manager, shard, payload):
        stage = manager.stages.upsert(payload)
        return cls(shard=shard, payload=payload, stage=stage)


@register
class StageInstanceUpdateEvent(BaseEvent):
    __event_name__ = 'STAGE_INSTANCE_UPDATE'
    __fields__ = (*BaseEvent.__fields__, 'stage')

    @classmethod
    async def execute(cls, manager, shard, payload):
        stage = manager.stages.upsert(payload)
        return cls(shard=shard, payload=payload, stage=stage)


@register
class StageInstanceDeleteEvent(BaseEvent):
    __event_name__ = 'STAGE_INSTANCE_DELETE'
    __fields__ = (*BaseEvent.__fields__, 'stage')

    @classmethod
    async def execute(cls, manager, shard, payload):
        stage = manager.stages.upsert(payload)
        stage._delete()
        return cls(shard=shard, payload=payload, stage=stage)


_base_fields = ('shard', 'payload')

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
