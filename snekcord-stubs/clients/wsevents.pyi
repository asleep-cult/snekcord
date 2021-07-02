from __future__ import annotations

import typing as t

from .wsclient import WebSocketClient
from ..objects.channelobject import DMChannel, GuildChannel, TextChannel
from ..objects.guildobject import Guild, GuildBan
from ..objects.inviteobject import Invite
from ..objects.memberobject import GuildMember
from ..objects.messageobject import Message
from ..objects.reactionsobject import Reactions
from ..objects.roleobject import Role
from ..objects.stageobject import StageInstance
from ..objects.userobject import User
from ..typedefs import Json
from ..ws.shardws import Shard

__all__ = ('ChannelCreateEvent', 'ChannelUpdateEvent', 'ChannelDeleteEvent',
           'ChannelPinsUpdateEvent', 'GuildReceiveEvent',
           'GuildAvailableEvent', 'GuildJoinEvent', 'GuildUpdateEvent',
           'GuildUnavailableEvent', 'GuildDeleteEvent', 'GuildBanAddEvent',
           'GuildBanRemoveEvent', 'GuildEmojisUpdateEvent',
           'GuildIntegrationsUpdateEvent', 'GuildMemberAddEvent',
           'GuildMemberUpdateEvent', 'GuildMemberRemoveEvent',
           'GuildRoleCreateEvent', 'GuildRoleUpdateEvent',
           'GuildRoleDeleteEvent', 'IntegrationCreateEvent',
           'IntegrationUpdateEvent', 'IntegrationDeleteEvent',
           'InviteCreateEvent', 'InviteDeleteEvent', 'MessageCreateEvent',
           'MessageUpdateEvent', 'MessageDeleteEvent',
           'MessageDeleteBulkEvent', 'MessageReactionAddEvent',
           'StageInstanceCreateEvent', 'StageInstanceUpdateEvent',
           'StageInstanceDeleteEvent')

T = t.TypeVar('T')


class WebSocketEvents(t.TypedDict):
    CHANNEL_CREATE: type[ChannelCreateEvent]
    CHANNEL_UPDATE: type[ChannelUpdateEvent]
    CHANNEL_DELETE: type[ChannelDeleteEvent]
    CHANNEL_PINS_UPDATE: type[ChannelPinsUpdateEvent]
    GUILD_RECEIVE: type[GuildReceiveEvent]
    GUILD_AVAILABLE: type[GuildAvailableEvent]
    GUILD_JOIN: type[GuildJoinEvent]
    GUILD_UPDATE: type[GuildUpdateEvent]
    GUILD_UNAVAILABLE: type[GuildUnavailableEvent]
    GUILD_DELETE: type[GuildDeleteEvent]
    GUILD_BAN_ADD: type[GuildBanAddEvent]
    GUILD_BAN_REMOVE: type[GuildBanRemoveEvent]
    GUILD_EMOJIS_UPDATE: type[GuildEmojisUpdateEvent]
    GUILD_INTEGRATIONS_UPDATE: type[GuildIntegrationsUpdateEvent]
    GUILD_MEMBER_ADD: type[GuildMemberAddEvent]
    GUILD_MEMBER_UPDATE: type[GuildMemberUpdateEvent]
    GUILD_MEMBER_REMOVE: type[GuildMemberRemoveEvent]
    GUILD_ROLE_CREATE: type[GuildRoleCreateEvent]
    GUILD_ROLE_UPDATE: type[GuildRoleUpdateEvent]
    GUILD_ROLE_DELETE: type[GuildRoleDeleteEvent]
    INTEGRATION_CREATE: type[IntegrationCreateEvent]
    INTEGRATION_UPDATE: type[IntegrationUpdateEvent]
    INTEGRATION_DELETE: type[IntegrationDeleteEvent]
    INVITE_CREATE: type[InviteCreateEvent]
    INVITE_DELETE: type[InviteDeleteEvent]
    MESSAGE_CREATE: type[MessageCreateEvent]
    MESSAGE_UPDATE: type[MessageUpdateEvent]
    MESSAGE_DELETE: type[MessageDeleteEvent]
    MESSAGE_DELETE_BULK: type[MessageDeleteBulkEvent]
    MESSAGE_REACTION_ADD: type[MessageReactionAddEvent]
    STAGE_INSTANCE_CREATE: type[StageInstanceCreateEvent]
    STAGE_INSTANCE_UPADTE: type[StageInstanceUpdateEvent]
    STAGE_INSTANCE_DELETE: type[StageInstanceDeleteEvent]


WS_EVENTS: WebSocketEvents


class BaseEvent():
    _event_name_: t.ClassVar[str]
    _fields_: t.ClassVar[tuple[str, ...]]

    shard: Shard
    data: Json

    def __init__(self, **kwargs: t.Any) -> None: ...

    @classmethod
    def execute(cls: type[T], client: WebSocketClient, shard: Shard, data: Json) -> T: ...

    @property
    def partial(self) -> bool: ...


class ChannelCreateEvent(BaseEvent):
    channel: DMChannel | GuildChannel


class ChannelUpdateEvent(BaseEvent):
    channel: DMChannel | GuildChannel


class ChannelDeleteEvent(BaseEvent):
    channel: DMChannel | GuildChannel


class ChannelPinsUpdateEvent(BaseEvent):
    channel: TextChannel | None


class GuildReceiveEvent(BaseEvent):
    guild: Guild


class GuildAvailableEvent(BaseEvent):
    guild: Guild


class GuildJoinEvent(BaseEvent):
    guild: Guild


class GuildUpdateEvent(BaseEvent):
    guild: Guild


class GuildUnavailableEvent(BaseEvent):
    guild: Guild


class GuildDeleteEvent(BaseEvent):
    guild: Guild


class GuildBanAddEvent(BaseEvent):
    ban: GuildBan | None
    guild: Guild | None


class GuildBanRemoveEvent(BaseEvent):
    ban: GuildBan | None
    guild: Guild | None


class GuildEmojisUpdateEvent(BaseEvent):
    guild: Guild | None


class GuildIntegrationsUpdateEvent(BaseEvent):
    pass


class GuildMemberAddEvent(BaseEvent):
    guild: Guild | None
    member: GuildMember | None


class GuildMemberUpdateEvent(BaseEvent):
    guild: Guild | None
    member: GuildMember | None


class GuildMemberRemoveEvent(BaseEvent):
    guild: Guild | None
    member: GuildMember | None
    user: User


class GuildRoleCreateEvent(BaseEvent):
    guild: Guild | None
    role: Role | None


class GuildRoleUpdateEvent(BaseEvent):
    guild: Guild | None
    role: Role | None


class GuildRoleDeleteEvent(BaseEvent):
    guild: Guild | None
    role: Role | None


class IntegrationCreateEvent(BaseEvent):
    pass


class IntegrationUpdateEvent(BaseEvent):
    pass


class IntegrationDeleteEvent(BaseEvent):
    pass


class InviteCreateEvent(BaseEvent):
    invite: Invite


class InviteDeleteEvent(BaseEvent):
    invite: Invite | None


class MessageCreateEvent(BaseEvent):
    channel: TextChannel | None
    message: Message | None


class MessageUpdateEvent(BaseEvent):
    channel: TextChannel | None
    message: Message | None


class MessageDeleteEvent(BaseEvent):
    channel: TextChannel | None
    message: Message | None


class MessageDeleteBulkEvent(BaseEvent):
    channel: TextChannel | None
    messages: list[Message]


class MessageReactionAddEvent(BaseEvent):
    channel: TextChannel | None
    message: Message | None
    reactions: Reactions | None
    user: User | None


class StageInstanceCreateEvent(BaseEvent):
    stage: StageInstance


class StageInstanceUpdateEvent(BaseEvent):
    stage: StageInstance


class StageInstanceDeleteEvent(BaseEvent):
    stage: StageInstance
