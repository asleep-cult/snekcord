from ..snowflake import Snowflake

__all__ = []

WS_EVENTS = {}
WS_EVENTS_INTENTS = {}


def register(name, *, intent=None):
    def wrapped(cls):
        __all__.append(cls.__name__)

        nonlocal name
        name = name.lower()

        WS_EVENTS[name] = cls.execute

        if intent is not None:
            WS_EVENTS_INTENTS[name] = intent.lower()
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
        fields = ', '.join(getattr(self, field) for field in self._fields_ if field != 'payload')
        return f'<{self.__class__.__name__} {fields}>'

    @classmethod
    async def execute(cls, client, shard, payload):
        raise NotImplementedError

    @property
    def partial(self):
        return False


@register('CHANNEL_CREATE', intent='GUILDS')
class ChannelCreateEvent(BaseEvent):
    _fields_ = ('channel',)

    @classmethod
    async def execute(cls, client, shard, payload):
        channel = client.channels.upsert(payload)
        return cls(shard=shard, payload=payload, channel=channel)


@register('CHANNEL_UPDATE', intent='GUILDS')
class ChannelUpdateEvent(BaseEvent):
    _fields_ = ('channel',)

    @classmethod
    async def execute(cls, client, shard, payload):
        channel = client.channels.upsert(payload)
        return cls(shard=shard, payload=payload, channel=channel)


@register('CHANNEL_DELETE', intent='GUILDS')
class ChannelDeleteEvent(BaseEvent):
    _fields_ = ('channel',)

    @classmethod
    async def execute(cls, client, shard, payload):
        channel = client.channels.upsert(payload)
        channel._delete()
        return cls(shard=shard, payload=payload, channel=channel)


class ChannelPinsUpdate(BaseEvent):
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


@register('DM_CHANNEL_PINS_UPDATE', intent='DM_MESSAGES')
class DMChannelPinsUpdateEvent(ChannelPinsUpdate):
    pass


@register('GUILD_CHANNEL_PINS_UPDATE', intent='GUILD_MESSAGES')
class GuildChannelPinsUpdateEvent(ChannelPinsUpdate):
    pass


@register('GUILD_CREATE', intent='GUILDS')
class GuildCreateEvent(BaseEvent):
    _fields_ = ('guild', 'from_unavailable', 'joined')

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        return cls(
            shard=shard, payload=payload, guild=guild,
            from_unavailable=payload.pop('_from_unavailable_'), joined=payload.pop('_joined_')
        )


@register('GUILD_UPDATE', intent='GUILDS')
class GuildUpdateEvent(BaseEvent):
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register('GUILD_UNAVAILABLE', intent='GUILDS')
class GuildUnavailableEvent(BaseEvent):
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        return cls(shard=shard, payload=payload, guild=guild)


@register('GUILD_DELETE', intent='GUILDS')
class GuildDeleteEvent(BaseEvent):
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.upsert(payload)
        guild._delete()
        return cls(shard=shard, payload=payload, guild=guild)


@register('GUILD_BAN_ADD', intent='GUILD_BANS')
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


@register('GUILD_BAN_REMOVE', intent='GUILD_BANS')
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


@register('GUILD_EMOJIS_UPDATE', intent='GUILD_EMOJIS_AND_STICKERS')
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
                guild.emojis[emoji_id]._delete()

        return cls(shard=shard, payload=payload, guild=guild)

    @property
    def partial(self):
        return self.guild is None


@register('GUILD_STICKERS_UPDATE', intent='GUILD_EMOJIS_AND_STICKERS')
class GuildStickersUpdate(BaseEvent):
    _fields_ = ('guild',)

    @classmethod
    async def execute(cls, client, shard, payload):
        guild = client.guilds.get(Snowflake(payload['guild_id']))

        if guild is not None:
            stickers = set()

            for sticker in payload['stickers']:
                stickers.add(guild.stickers.upsert(sticker).id)

            for sticker_id in set(guild.stickers.keys()) - stickers:
                guild.stickers[sticker_id]._delete()

        return cls(shard=shard, payload=payload, guild=guild)

    @property
    def partial(self):
        return self.guild is None


# @register('GUILD_INTEGRATIONS_UPDATE', intent='GUILD_INTEGRATIONS')
class GuildIntegrationsUpdateEvent(BaseEvent):
    _fields_ = ('guild',)


@register('GUILD_MEMBER_ADD', intent='GUILD_MEMBERS')
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


@register('GUILD_MEMBER_UPDATE', intent='GUILD_MEMBERS')
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


@register('GUILD_MEMBER_REMOVE', intent='GUILD_MEMBERS')
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


@register('GUILD_ROLE_CREATE', intent='GUILDS')
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


@register('GUILD_ROLE_UPDATE', intent='GUILDS')
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


@register('GUILD_ROLE_DELETE', intent='GUILDS')
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


# @register('INTEGRATION_CREATE', intent='GUILD_INTEGRATIONS')
class IntegrationCreateEvent(BaseEvent):
    pass


# @register('INTEGRATION_UPDATE', intent='GUILD_INTEGRATIONS')
class IntegrationUpdateEvent(BaseEvent):
    pass


# @register('INTEGRATION_DELETE', intent='GUILD_INTEGRATIONS')
class IntegrationDeleteEvent(BaseEvent):
    pass


@register('INVITE_CREATE', intent='GUILD_INVITES')
class InviteCreateEvent(BaseEvent):
    _fields_ = ('invite',)

    @classmethod
    async def execute(cls, client, shard, payload):
        invite = client.invites.upsert(payload)
        return cls(shard=shard, payload=payload, invite=invite)


@register('INVITE_DELETE', intent='GUILD_INVITES')
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


class MessageCreateEvent(BaseEvent):
    _fields_ = ('channel', 'message')

    @classmethod
    async def execute(cls, client, shard, payload):
        message = None
        channel = client.channels.get(Snowflake(payload['channel_id']))

        if channel is not None:
            message = channel.messages.upsert(payload)
            channel._json_data_['last_message_id'] = message._json_data_['id']

        return cls(shard=shard, payload=payload, channel=channel, message=message)

    @property
    def partial(self):
        return self.channel is None


@register('DIRECT_MESSAGE_CREATE', intent='DIRECT_MESSAGES')
class DirectMessageCreateEvent(MessageCreateEvent):
    pass


@register('GUILD_MESSAGE_CREATE', intent='GUILD_MESSAGES')
class GuildMessageCreateEvent(MessageCreateEvent):
    pass


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


@register('DIRECT_MESSAGE_UPDATE', intent='DIRECT_MESSAGES')
class DirectMessageUpdateEvent(MessageUpdateEvent):
    pass


@register('GUILD_MESSAGE_UPDATE', intent='GUILD_MESSAGES')
class GuildMessageCreateEvent(MessageUpdateEvent):
    pass


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


@register('DIRECT_MESSAGE_CREATE', intent='DIRECT_MESSAGES')
class DirectMessageCreateEvent(MessageCreateEvent):
    pass


@register('GUILD_MESSAGE_CREATE', intent='GUILD_MESSAGES')
class GuildMessageCreateEvent(MessageCreateEvent):
    pass


@register('GUILD_MESSAGE_DELETE_BULK', intent='GUILD_MESSAGES')
class GuildMessageDeleteBulkEvent(BaseEvent):
    _fields_ = ('channel', 'messages')

    @classmethod
    async def execute(cls, client, shard, payload):
        messages = []
        channel = client.channels.get(Snowflake(payload['channel_id']))

        if channel is not None:
            for message in payload['ids']:
                message = channel.messages.get(message)

                if message is not None:
                    messages.append(message)

        return cls(shard=shard, payload=payload, channel=channel, messages=messages)

    @property
    def partial(self):
        return self.channel is None


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


@register('DIRECT_MESSAGE_REACTION_ADD', intent='DIRECT_MESSAGES')
class DirectMessageReactionAddEvent(MessageReactionAddEvent):
    pass


@register('GUILD_MESSAGE_REACTION_ADD', intent='GUILD_MESSAGES')
class GuildMessageReactionAddEvent(MessageReactionAddEvent):
    pass


@register('STAGE_INSTANCE_CREATE', intent='GUILDS')
class StageInstanceCreateEvent(BaseEvent):
    _fields_ = ('stage',)

    @classmethod
    async def execute(cls, client, shard, payload):
        stage = client.stage_instances.upsert(payload)
        return cls(shard=shard, payload=payload, stage=stage)


@register('STAGE_INSTANCE_UPDATE', intent='GUILDS')
class StageInstanceUpdateEvent(BaseEvent):
    _fields_ = ('stage',)

    @classmethod
    async def execute(cls, client, shard, payload):
        stage = client.stage_instances.upsert(payload)
        return cls(shard=shard, payload=payload, stage=stage)


@register('STAGE_INSTANCE_DELETE', intent='GUILDS')
class StageInstanceDeleteEvent(BaseEvent):
    _fields_ = ('stage',)

    @classmethod
    async def execute(cls, client, shard, payload):
        stage = client.stage_instances.upsert(payload)
        stage._delete()
        return cls(shard=shard, payload=payload, stage=stage)
