from __future__ import annotations

import enum
import typing

from ..enums import convert_enum
from ..exceptions import UnsupportedDataError
from ..rest.endpoints import GET_GATEWAY, GET_GATEWAY_BOT
from ..snowflake import Snowflake
from ..websockets import Shard
from .bases import BaseAPI

if typing.TYPE_CHECKING:
    from typing_extensions import NotRequired

    from ..json import JSONObject, JSONType
    from .presence import RawActivity

OpcodeT = typing.TypeVar('OpcodeT')
DataT = typing.TypeVar('DataT')


class GatewayCloseCode(enum.IntEnum):
    UNKNOWN_ERROR = 4000
    UNKNOWN_OPCODE = 4001
    DECODE_ERROR = 4002
    NOT_AUTHENTICATED = 4003
    AUTHENTICATION_FAILED = 4004
    ALREADY_AUTHENTICATED = 4005
    INVALID_SEQUENCE = 4007
    RATELIMITED = 4008
    SESSION_TIMED_OUT = 4009
    INVALID_SHARD = 4010
    SHARDING_REQUIRED = 4011
    INVALID_API_VERSION = 4012
    INVALID_INTENTS = 4013
    DISALLOWED_INTENTS = 4014


class GatewayIntents(enum.IntFlag):
    NONE = 0

    GUILDS = 1 << 0
    GUILD_MEMBERS = 1 << 1
    GUILD_BANS = 1 << 2
    GUILD_EMOJIS_AND_STICKERS = 1 << 3
    GUILD_INTEGRATIONS = 1 << 4
    GUILD_WEBHOOKS = 1 << 5
    GUILD_INVITES = 1 << 6
    GUILD_VOICE_STATES = 1 << 7
    GUILD_PRESENCES = 1 << 8
    GUILD_MESSAGES = 1 << 9
    GUILD_MESSAGE_REACTIONS = 1 << 10
    GUILD_MESSAGE_TYPING = 1 << 11
    DIRECT_MESSAGES = 1 << 12
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    DIRECT_MESSAGE_TYPING = 1 << 14
    GUILD_SCHEDULED_EVENTS = 1 << 16

    UNPRIVILEGED = (
        GUILDS
        | GUILD_BANS
        | GUILD_EMOJIS_AND_STICKERS
        | GUILD_INTEGRATIONS
        | GUILD_WEBHOOKS
        | GUILD_INVITES
        | GUILD_VOICE_STATES
        | GUILD_MESSAGES
        | GUILD_MESSAGE_REACTIONS
        | GUILD_MESSAGE_TYPING
        | DIRECT_MESSAGES
        | DIRECT_MESSAGE_REACTIONS
        | DIRECT_MESSAGE_TYPING
        | GUILD_SCHEDULED_EVENTS
    )


class RawGateway(typing.TypedDict):
    url: str


class RawSessionStartLimit(typing.TypedDict):
    total: int
    remaining: int
    reset_after: int
    max_concurrency: int


class RawBotGateway(RawGateway):
    shards: str
    session_start_limit: RawSessionStartLimit


class GatewayOpcode(enum.IntEnum):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11


class RawGatewayPayload(typing.TypedDict):
    op: typing.Union[GatewayOpcode, int]
    d: typing.Optional[JSONType]
    s: typing.Optional[int]
    t: typing.Optional[str]


class RawDispatchPayload(typing.TypedDict):
    op: typing.Literal[GatewayOpcode.DISPATCH]
    d: JSONObject
    s: int
    t: str


class RawPayload(typing.TypedDict, typing.Generic[OpcodeT, DataT]):
    op: OpcodeT
    d: DataT


class RawConnectionProperties(typing.TypedDict):
    os: str
    browser: str
    device: str


class RawIdentifyData(typing.TypedDict):
    token: str
    properties: RawConnectionProperties
    compress: NotRequired[bool]
    large_threshold: NotRequired[int]
    shard: NotRequired[typing.Tuple[int, int]]
    presense: NotRequired[RawPresenceUpdateData]
    intents: int


class RawPresenceUpdateData(typing.TypedDict):
    since: typing.Optional[int]
    activities: typing.List[RawActivity]
    status: str
    afk: bool


class RawVoiceStateUpdateData(typing.TypedDict):
    guild_id: Snowflake
    channel_id: typing.Optional[Snowflake]
    self_mute: bool
    self_deaf: bool


class RawRequestGuildMembersData(typing.TypedDict):
    guild_id: Snowflake
    query: NotRequired[str]
    limit: int
    presences: NotRequired[bool]
    user_ids: NotRequired[typing.List[Snowflake]]
    nonce: NotRequired[str]


class RawHelloData(typing.TypedDict):
    heartbeat_interval: int


RawHeartbeatPayload = RawPayload[typing.Literal[GatewayOpcode.HEARTBEAT], None]
RawIdentifyPayload = RawPayload[typing.Literal[GatewayOpcode.IDENTIFY], RawIdentifyData]
RawPresenceUpdatePayload = RawPayload[
    typing.Literal[GatewayOpcode.PRESENCE_UPDATE], RawPresenceUpdateData
]
RawVoiceStateUpdatePayload = RawPayload[
    typing.Literal[GatewayOpcode.VOICE_STATE_UPDATE], RawVoiceStateUpdateData
]
RawReconnectPayload = RawPayload[typing.Literal[GatewayOpcode.RECONNECT], None]
RawRequestGuildMembersPayload = RawPayload[
    typing.Literal[GatewayOpcode.REQUEST_GUILD_MEMBERS], RawRequestGuildMembersData
]
RawInvalidSessionPayload = RawPayload[typing.Literal[GatewayOpcode.INVALID_SESSION], bool]
RawHelloPayload = RawPayload[typing.Literal[GatewayOpcode.HELLO], RawHelloData]
RawHeartbeatACKPayload = RawPayload[typing.Literal[GatewayOpcode.HEARTBEAT_ACK], None]

RawGatewayPayloadTypes = typing.Union[
    RawGatewayPayload,
    RawDispatchPayload,
    RawHeartbeatPayload,
    RawIdentifyPayload,
    RawPresenceUpdatePayload,
    RawVoiceStateUpdatePayload,
    RawReconnectPayload,
    RawRequestGuildMembersPayload,
    RawInvalidSessionPayload,
    RawHelloPayload,
    RawHeartbeatACKPayload,
]


class GatewayAPI(BaseAPI):
    def sanitize_gateway(self, data: JSONObject) -> RawGateway:
        return {'url': data['url']}

    def sanitize_session_start_limit(self, data: JSONObject) -> RawSessionStartLimit:
        return {
            'total': data['total'],
            'remaining': data['remaining'],
            'reset_after': data['reset_after'],
            'max_concurrency': data['max_concurrency'],
        }

    def sanitize_bot_gateway(self, data: JSONObject) -> RawBotGateway:
        start_limit = self.sanitize_session_start_limit(data['session_start_limit'])

        return {
            'url': data['url'],
            'shards': data['shards'],
            'session_start_limit': start_limit,
        }

    def sanitize_payload(self, data: JSONObject) -> RawGatewayPayloadTypes:
        opcode = convert_enum(GatewayOpcode, data['op'])

        if opcode is GatewayOpcode.DISPATCH:
            return {
                'op': GatewayOpcode.DISPATCH,
                'd': data['d'],
                's': data['s'],
                't': data['t'],
            }

        elif opcode is GatewayOpcode.HEARTBEAT:
            return {
                'op': GatewayOpcode.HEARTBEAT,
                'd': None,
            }

        elif opcode is GatewayOpcode.RECONNECT:
            return {
                'op': GatewayOpcode.RECONNECT,
                'd': None,
            }

        elif opcode is GatewayOpcode.INVALID_SESSION:
            return {
                'op': GatewayOpcode.INVALID_SESSION,
                'd': data['d'],
            }

        elif opcode is GatewayOpcode.HELLO:
            return {
                'op': GatewayOpcode.HELLO,
                'd': {
                    'heartbeat_interval': data['d']['heartbeat_interval'],
                },
            }

        elif opcode is GatewayOpcode.HEARTBEAT_ACK:
            return {
                'op': GatewayOpcode.HEARTBEAT_ACK,
                'd': None,
            }

        return {
            'op': opcode,
            'd': data.get('d'),
            's': data.get('s'),
            't': data.get('t'),
        }

    async def get_gateway(self) -> RawGateway:
        data = await self.request_api(GET_GATEWAY)

        if not isinstance(data, dict):
            raise UnsupportedDataError(self.client.rest, data)

        return self.sanitize_gateway(data)

    async def get_gateway_bot(self) -> RawBotGateway:
        data = await self.request_api(GET_GATEWAY_BOT)

        if not isinstance(data, dict):
            raise UnsupportedDataError(self.client.rest, data)

        return self.sanitize_bot_gateway(data)

    async def create_shard(self, url: str, shard_id: int) -> Shard:
        return Shard(self.client, url, shard_id)
