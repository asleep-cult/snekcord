import asyncio
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
    guild_id: Snowflake = JsonField('guild_id', Snowflake, str)
    channel_id: Snowflake = JsonField('channel_id', Snowflake, str)
    user_id: Snowflake = JsonField('user_id', Snowflake, str)
    _member: dict = JsonField('member')
    session_id: str = JsonField('session_id')
    deaf: bool = JsonField('deaf')
    mute: bool = JsonField('mute')
    self_deaf: bool = JsonField('self_deaf')
    self_mute: bool = JsonField('self_mute')
    self_stream: bool = JsonField('self_stream')
    self_video: bool = JsonField('self_video')
    suppress: bool = JsonField('suppress')

    def __init__(self, voice_channel):
        self.voice_channel = voice_channel
        self.guild = voice_channel.guild

        if self._member is not None:
            self.member = self.guild.members._add(self._member)

        del self._member


class VoiceServerUpdate(JsonStructure):
    token: str = JsonField('token')
    guild_id: Snowflake = JsonField('guild_id', Snowflake, str)
    endpoint: str = JsonField('endpoint')


class VoiceConnection:
    def __init__(self, voice_state: VoiceState, voice_server_update: VoiceServerUpdate):
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
        self.loop: asyncio.AbstractEventLoop = self._client.loop
        self.mode = []
        self.ip = None
        self.port = None
        self.udp_ip = None
        self.udp_port = None
        self.transport = None
        self.protocol = None
        self.ssrc = None

    async def connect(self):
        await self.ws.connect()

    async def dispatch(self, resp):
        if resp.opcode == VoiceConnectionOpcode.READY:
            self.ip = resp.data['ip']
            self.port = resp.data['port']
            self.mode = resp.data['modes'][0]
            self.ssrc = resp.data['ssrc']
            
            buffer = bytearray(70)
            struct.pack_into('!I', buffer, 4, self.ssrc)

            self.transport, self.protocol = await self.loop.create_datagram_endpoint(VoiceUDPProtocol, remote_addr=(self.ip, self.port))

            self.protocol.voice_connection = self

            self.transport.sendto(buffer)

            data = await self.protocol.first_datagram_received

            end = data.index(0, 4)
            udp_ip = data[4:end]
            self.udp_ip = udp_ip.decode()

            udp_port = data[-2:]
            self.udp_port = int.from_bytes(udp_port, 'big')

            await self.ws.select()

        else:
            print(resp.data)