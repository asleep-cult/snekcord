import struct

from .connection import (
    VoiceWSProtocol,
    VoiceUDPProtocol,
    VoiceConnectionOpcode
)

from .utils import (
    JsonStructure,
    JsonField,
    Snowflake
)


class VoiceState(JsonStructure):
    __json_fields__ = {
        'guild_id': JsonField('guild_id', Snowflake, str),
        'channel_id': JsonField('channel_id', Snowflake, str),
        'user_id': JsonField('user_id', Snowflake, str),
        '_member': JsonField('member'),
        'session_id': JsonField('session_id'),
        'deaf': JsonField('deaf'),
        'mute': JsonField('mute'),
        'self_deaf': JsonField('self_deaf'),
        'self_mute': JsonField('self_mute'),
        'self_stream': JsonField('self_stream'),
        'self_video': JsonField('self_video'),
        'suppress': JsonField('suppress'),
    }

    guild_id: Snowflake
    channel_id: Snowflake
    user_id: Snowflake
    _member: dict
    session_id: str
    deaf: bool
    mute: bool
    self_deaf: bool
    self_mute: bool
    self_stream: bool
    self_video: bool
    suppress: bool

    def __init__(self, voice_channel):
        self.voice_channel = voice_channel
        self.guild = voice_channel.guild

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)

        if self._member is not None:
            self.member = self.guild.members._add(self._member)


class VoiceServerUpdate(JsonStructure):
    __json_fields__ = {
        'token': JsonField('token'),
        'guild_id': JsonField('guild_id', Snowflake, str),
        'endpoint': JsonField('endpoint'),
    }

    token: str
    guild_id: Snowflake
    endpoint: str


class VoiceConnection:
    def __init__(
        self,
        voice_state: VoiceState,
        voice_server_update: VoiceServerUpdate
    ):
        self.token = voice_server_update.token
        self.guild_id = voice_server_update.guild_id
        endpoint = voice_server_update.endpoint + '?v=4'
        if not endpoint.startswith('wss://'):
            self.endpoint = 'wss://' + endpoint
        else:
            self.endpoint = endpoint
        self.voice_state = voice_state
        self.voice_channel = voice_state.voice_channel
        self._client = self.voice_channel._state._client
        self.ws = VoiceWSProtocol(self)
        self.loop = self._client.loop
        self.mode = []
        self.ip = None
        self.port = None
        self.transport = None
        self.protocol = None
        self.ssrc = None

    async def connect(self):
        await self.ws.connect()

    async def dispatch(self, resp):
        print(resp.data)
        if resp.opcode == VoiceConnectionOpcode.READY:
            self.ip = resp.data['ip']
            self.port = resp.data['port']
            self.mode = resp.data['modes'][0]
            self.ssrc = resp.data['ssrc']

            buffer = bytearray(70)
            struct.pack_into('!I', buffer, 4, self.ssrc)

            self.transport, self.protocol = \
                await self.loop.create_datagram_endpoint(
                    VoiceUDPProtocol, remote_addr=(self.ip, self.port)
                )
            self.protocol.loop = self.loop
            self.protocol.voice_connection = self

            self.transport.sendto(buffer)
        else:
            print(resp.data)
