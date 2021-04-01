import struct

import nacl.secret

from . import structures
from .events import EventPusher
from .connection import VoiceWebSocket, VoiceDatagramProtocol, VoiceConnectionOpcode


class VoiceState(structures.VoiceState):
    def __init__(self, voice_channel):
        self.voice_channel = voice_channel
        self.guild = voice_channel.guild

    def _update(self, *args, **kwargs):
        super()._update(*args, **kwargs)

        if self._member is not None:
            self.member = self.guild.members.append(self._member)


class VoiceConnection(EventPusher):
    def __init__(self, loop, voice_state, voice_server_update):
        super().__init__(loop)

        self.voice_state = voice_state
        self.voice_server_update = voice_server_update

        endpoint = voice_server_update.endpoint + '/?v=4'
        if not endpoint.startswith('wss://'):
            self.ws_endpoint = 'wss://' + endpoint
        else:
            self.ws_endpoint = endpoint

        self.receiver = None

        self.ws = VoiceWebSocket(self.ws_endpoint, self)

        self.mode = None
        self.ssrc = None
        self.secret_key = None
        self.secret_box = None

        self.dgram_endpoint = None
        self.dgram_transport = None

        self.selected = False

        self.register_listener('op_ready', self.op_ready)
        self.register_listener('op_session_description', self.op_session_description)
        self.register_listener('datagram_received', self.datagram_received)

    async def connect(self):
        await self.ws.connect(ssl=True)

    async def op_ready(self, payload):
        self.dgram_endpoint = payload['ip'], payload['port']
        self.mode = 'xsalsa20_poly1305'
        self.ssrc = payload['ssrc']

        buffer = bytearray(70)
        struct.pack_into('!I', buffer, 4, self.ssrc)

        self.transport, self.protocol = await self.loop.create_datagram_endpoint(
            lambda: VoiceDatagramProtocol(self), remote_addr=self.dgram_endpoint
        )
        self.transport.sendto(buffer)

    async def op_session_description(self, payload):
        self.secret_key = bytes(payload['secret_key'])
        self.secret_box = nacl.secret.SecretBox(self.secret_key)

    async def datagram_received(self, data):
        if not self.selected:
            end = data.index(0, 4)
            self.ip = data[4:end].decode()
            self.port = int.from_bytes(data[-2:], 'big')

            self.ws.select(self.ip, self.port, self.mode)
            self.selected = True
        elif self.receiver is not None:
            await self.receiver.received(data)
