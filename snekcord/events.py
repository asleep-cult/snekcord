from collections import namedtuple

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
