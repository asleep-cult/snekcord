import struct

from . import structures
from .connection import VoiceUDPProtocol, VoiceWSProtocol
from .enums import VoiceConnectionOpcode


class VoiceState(structures.VoiceState):
    def __init__(self, voice_channel):
        self.voice_channel = voice_channel
        self.guild = voice_channel.guild

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)

        if self._member is not None:
            self.member = self.guild.members._add(self._member)


class VoiceConnection:
    def __init__(self, voice_state, voice_server_update):
        self.token = voice_server_update.token
        self.guild_id = voice_server_update.guild_id
        endpoint = voice_server_update.endpoint + '?v=4'
        if not endpoint.startswith('wss://'):
            self.endpoint = 'wss://' + endpoint
        else:
            self.endpoint = endpoint
        self.voice_state = voice_state
        self.voice_channel = voice_state.voice_channel
        self.client = self.voice_channel._state.client
        self.ws = VoiceWSProtocol(self)
        self.loop = self.client.loop
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
