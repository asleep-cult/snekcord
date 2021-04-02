import os
import http
import base64
import json
import time
import platform
import functools
import asyncio
import urllib.parse

from enum import IntEnum

from .events import EventPusher
from .utils import JsonStructure, JsonField, cstruct
from .exceptions import BadWsHttpResponse


class WebsocketOpcode(IntEnum):
    CONT = 0x00
    TEXT = 0x01
    BINARY = 0x02
    CLOSE = 0x08
    PING = 0x09
    PONG = 0x0A


class WebsocketFrame(cstruct):
    byteorder = '>'
    fbyte: cstruct.UnsignedChar
    sbyte: cstruct.UnsignedChar

    def __init__(
        self, data: bytearray, *, opcode: int = WebsocketOpcode.TEXT, fin: bool =True,
        rsv1: bool = False, rsv2: bool = False, rsv3: bool = False, masked: bool=True
    ): # Pretty sure `data` is bytearray
        self.data = data
        self.opcode = opcode
        self.fin = fin
        self.rsv1 = rsv1
        self.rsv2 = rsv2
        self.rsv3 = rsv3
        self.masked = masked

    def get_fin(self):
        return self.fbyte & 0b10000000

    def get_rsv1(self):
        return self.fbyte & 0b01000000

    def get_rsv2(self):
        return self.fbyte & 0b00100000

    def get_rsv3(self):
        return self.fbyte & 0b00010000

    def get_opcode(self):
        return self.fbyte & 0b00001111

    def get_masked(self):
        return self.sbyte & 0b10000000

    def get_length(self):
        return self.sbyte & 0b01111111

    @staticmethod
    def apply_mask(mask: bytearray, data: bytearray):
        for i in range(len(data)):
            data[i] ^= mask[i % 4]
        return data

    @classmethod
    def from_head(cls, head):
        self = cls.unpack(head)
        self.data = b''
        self.fin = self.get_fin()
        self.rsv1 = self.get_rsv1()
        self.rsv2 = self.get_rsv2()
        self.rsv3 = self.get_rsv3()
        self.opcode = self.get_opcode()
        self.masked = self.get_masked()
        self.length = self.get_length()
        return self

    def encode(self):
        data = self.data
        buffer = bytearray(2)

        if self.fin:
            buffer[0] |= 0b10000000

        if self.rsv1:
            buffer[0] |= 0b01000000

        if self.rsv2:
            buffer[0] |= 0b00100000

        if self.rsv3:
            buffer[0] |= 0b00010000

        buffer[0] |= self.opcode

        if self.masked:
            buffer[1] |= 0b10000000

        length = len(data)

        if length <= 125:
            buffer[1] |= length
        else:
            if length <= 0xFFFF:
                buffer[1] |= 126
                size = cstruct.UnsignedShort.size
            else:
                buffer[1] |= 127
                size = cstruct.UnsignedLongLong.size

            buffer.extend(length.to_bytes(size, 'big', signed=False))

        if self.masked:
            mask = os.urandom(4)
            buffer.extend(mask)
            data = self.apply_mask(mask, bytearray(self.data))

        buffer.extend(data)

        return buffer


class WebsocketProtocolState(IntEnum):
    WAITING_FBYTE = 0
    WAITING_SBYTE = 1
    WAITING_LENGTH = 2
    WAITING_DATA = 3


class WebsocketProtocol(asyncio.Protocol):
    def __init__(self, connection):
        self.connection = connection
        self.state = WebsocketProtocolState.WAITING_FBYTE
        self.head_buffer = bytearray(2)
        self.frame = None
        self.bytes_needed = 0
        self.length_buffer = b''
        self.headers = b''
        self.have_headers = asyncio.Event()

    def _check_position(self, position: int, data: bytearray):
        if position >= len(data):
            raise EOFError

    def _create_frames(self, data: bytearray):
        position = 0
        while True:
            self._check_position(position, data)

            if self.state == WebsocketProtocolState.WAITING_FBYTE:
                self.head_buffer[0] = data[position]
                position += 1
                self.state = WebsocketProtocolState.WAITING_SBYTE

            self._check_position(position, data)

            if self.state == WebsocketProtocolState.WAITING_SBYTE:
                self.head_buffer[1] = data[position]
                position += 1
                self.frame = WebsocketFrame.from_head(self.head_buffer)

                if self.frame.length > 125:
                    self.state = WebsocketProtocolState.WAITING_LENGTH

                    if self.frame.length == 126:
                        self.bytes_needed = cstruct.UnsignedShort.size
                    elif self.frame.length == 127:
                        self.bytes_needed = cstruct.UnsignedLongLong.size
                else:
                    self.bytes_needed = self.frame.length
                    self.state = WebsocketProtocolState.WAITING_DATA

            self._check_position(position, data)

            if self.state == WebsocketProtocolState.WAITING_LENGTH:
                length_bytes = data[position:position + self.bytes_needed]
                position += len(length_bytes)
                self.bytes_needed -= len(length_bytes)
                self.length_buffer += length_bytes

                if self.bytes_needed == 0:
                    self.frame.length = int.from_bytes(self.length_buffer, 'big', signed=False)
                    self.length_buffer = b''
                    self.bytes_needed = self.frame.length
                    self.state = WebsocketProtocolState.WAITING_DATA

            self._check_position(position, data)

            if self.state == WebsocketProtocolState.WAITING_DATA:
                data_bytes = data[position:position + self.bytes_needed]
                position += len(data_bytes)
                self.bytes_needed -= len(data_bytes)
                self.frame.data += data_bytes

                if self.bytes_needed == 0:
                    self.connection.push_event('ws_frame_receive', self.frame)
                    self.frame = None
                    self.state = WebsocketProtocolState.WAITING_FBYTE

            self._check_position(position, data)

    def create_frames(self, data: bytearray):
        try:
            self._create_frames(data)
        except EOFError:
            pass

    def data_received(self, data: bytearray):
        if not self.have_headers.is_set():
            try:
                index = data.index(b'\r\n\r\n') + 4
                self.headers += data[:index]
                self.have_headers.set()
                self.create_frames(data[index:])
            except ValueError:
                self.headers += data
        else:
            self.create_frames(data)


class DiscordResponse(JsonStructure):
    __json_fields__ = {
        'opcode': JsonField('op'),
        'sequence': JsonField('s'),
        'event_name': JsonField('t'),
        'data': JsonField('d')
    }


class BaseConnection(EventPusher):
    def __init__(self, endpoint, pusher: EventPusher, *, heartbeat_timeout: int = 10):
        super().__init__(pusher.loop)

        self.endpoint = endpoint
        self.loop = pusher.loop
        self.pusher = pusher

        self.register_listener('connection_stale', self.connection_stale)
        self.register_listener('ws_frame_receive', self.ws_frame_receive)
        self.register_listener('ws_receive', self.ws_receive)

        self.heartbeat_handler = HeartbeatHandler(self, timeout=heartbeat_timeout)

        self.transport = None
        self.protocol = None

        self.sec_ws_key = base64.b64encode(os.urandom(16))

    @property
    def heartbeat_payload(self):
        raise NotImplementedError

    async def connection_stale(self):
        raise NotImplementedError

    async def ws_receive(self, response):
        raise NotImplementedError

    def ws_frame_receive(self, frame):
        if frame.opcode == WebsocketOpcode.TEXT:
            response = DiscordResponse.unmarshal(frame.data)
            self.push_event('ws_receive', response)

    def form_headers(self, meth, path, headers):
        parts = ['%s %s HTTP/1.1' % (meth, path)]

        for name, value in headers.items():
            parts.append('%s: %s' % (name, value))

        parts.append('\r\n')

        return '\r\n'.join(parts).encode()

    def iter_headers(self):
        offset = 0
        while True:
            index = self.protocol.headers.index(b'\r\n', offset) + 2
            data = self.protocol.headers[offset:index]
            offset = index
            if data == b'\r\n':
                return
            yield [value.strip().lower() for value in data.split(b':', 1)]

    async def connect(self, **kwargs):
        headers = kwargs.pop('headers', {})

        url = urllib.parse.urlparse(self.endpoint)
        port = url.port or kwargs.pop('port', None)

        self.transport, self.protocol = await self.loop.create_connection(
            lambda: WebsocketProtocol(self), url.hostname, port, **kwargs
        )

        headers.update({
            'Host': '{}:{}'.format(url.hostname, port),
            'Connection': 'Upgrade',
            'Upgrade': 'websocket',
            'Sec-WebSocket-Key': self.sec_ws_key.decode(),
            'Sec-WebSocket-Version': 13
        })

        path = (url.path + url.params) or '/'
        self.transport.write(self.form_headers('GET', path, headers))

        await self.protocol.have_headers.wait()
        headers = self.iter_headers()
        status, = next(headers)

        status_code = status.split(b' ')[1].decode()
        if int(status_code) != http.HTTPStatus.SWITCHING_PROTOCOLS:
            raise BadWsHttpResponse(
                'status code',
                http.HTTPStatus.SWITCHING_PROTOCOLS,
                status_code
            )

        headers = dict(headers)

        connection = headers.get(b'connection').decode()
        if connection != 'upgrade':
            raise BadWsHttpResponse('connection', 'upgrade', connection)

        upgrade = headers.get(b'upgrade').decode()
        if upgrade != 'websocket':
            raise BadWsHttpResponse('upgrade', 'websocket', upgrade)

    def send_frame(self, frame):
        self.transport.write(frame.encode())

    def send(self, data, *args, **kwargs):
        frame = WebsocketFrame(data, *args, **kwargs)
        self.send_frame(frame)

    def send_json(self, data):
        self.send(json.dumps(data).encode())


class HeartbeatHandler:
    def __init__(self, connection, *, timeout=10):
        self.connection = connection
        self.loop = connection.loop
        self.timeout = timeout

        self.heartbeat_interval = float('inf')
        self.heartbeats_sent = 0
        self.heartbeats_acked = 0
        self.last_sent = float('inf')
        self.last_acked = float('inf')

        self.current_handle = None
        self.stopped = False

    def do_heartbeat(self):
        if self.stopped:
            return

        func = functools.partial(self.loop.create_task, self.send_heartbeat())
        self.current_handle = self.loop.call_later(self.heartbeat_interval, func)

    async def send_heartbeat(self):
        if self.stopped:
            return

        paylod = self.connection.heartbeat_payload
        self.last_sent = time.perf_counter()
        self.connection.send_json(paylod)

        # await self.wait_ack()

        self.do_heartbeat()

    async def wait_ack(self):
        try:
            await self.connection.wait(
                'heartbeat_ack',
                timeout=self.timeout,
            )
            self.last_acked = time.perf_counter()
            self.heartbeats_acked += 1
        except asyncio.TimeoutError:
            self.stop()
            self.connection.push_event('connection_stale')

    def start(self):
        self.loop.create_task(self.send_heartbeat())

    def stop(self):
        self.stopped = True
        if self.current_handle is not None:
            self.current_handle.cancel()

    @property
    def latency(self):
        return self.last_acked - self.last_sent


class ShardOpcode(IntEnum):
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


class Shard(BaseConnection):
    def __init__(self, shard_id, *args, ready_timeout=10, guild_create_timeout=10, **kwargs):
        self.id = shard_id
        self.ready_timeout = ready_timeout
        self.guild_create_timeout = guild_create_timeout
        self._guilds = set()
        super().__init__(*args, **kwargs)

    @property
    def identify_payload(self):
        payload = {
            'op': ShardOpcode.IDENTIFY,
            'd': {
                'token': self.pusher.token,
                # 'intents': self.manager.intents,
                'properties': {
                    '$os': platform.system(),
                    '$browser': 'wrapper-we-dont-name-for',
                    '$device': '^'
                }
            }
        }
        if self.pusher.multi_sharded:
            payload['shard'] = [self.id, len(self.pusher.shards)]
        return payload

    @property
    def heartbeat_payload(self):
        payload = {
            'op': ShardOpcode.HEARTBEAT,
            'd': None
        }
        return payload

    def _guilds_resolved(self, evnt):
        try:
            self._guilds.remove(evnt.guild.id)
        except KeyError:
            pass

        return not self._guilds

    async def connect(self, *args, **kwargs):
        ready_waiter = self.wait('ready', timeout=self.ready_timeout)
        guilds_waiter = self.pusher.wait(
            'guild_create',
            timeout=self.guild_create_timeout,
            filter=self._guilds_resolved
        )
        await super().connect(*args, **kwargs)

        data = await ready_waiter
        self.pusher.push_event('shard_ready_receive', self, data)

        for guild in data['guilds']:
            self._guilds.add(int(guild['id']))

        await guilds_waiter

        self.pusher.push_event('shard_ready', self)

    async def ws_receive(self, response):
        if response.opcode == ShardOpcode.HELLO:
            self.send_json(self.identify_payload)
            self.heartbeat_handler.heartbeat_interval = response.data['heartbeat_interval'] / 1000
            self.heartbeat_handler.start()
        elif response.opcode == ShardOpcode.HEARTBEAT_ACK:
            self.push_event('heartbeat_ack')
        elif response.opcode == ShardOpcode.DISPATCH:
            pusher = self if response.event_name in ('READY', 'RESUME') else self.pusher
            pusher.push_event(response.event_name, response.data)

    def update_voice_state(self, guild_id, channel_id, self_mute=False, self_deaf=False):
        payload = {
            'op': ShardOpcode.VOICE_STATE_UPDATE,
            'd': {
                'guild_id': guild_id,
                'channel_id': channel_id,
                'self_mute': self_mute,
                'self_deaf': self_deaf
            }
        }
        self.send_json(payload)
        return self.pusher.wait('VOICE_STATE_UPDATE'), self.pusher.wait('VOICE_SERVER_UPDATE')


class VoiceConnectionOpcode(IntEnum):
    IDENTIFY = 0
    SELECT = 1
    READY = 2
    HEARTBEAT = 3
    SESSION_DESCRIPTION = 4
    SPEAKING = 5
    HEARTBEAT_ACK = 6
    RESUME = 7
    HELLO = 8
    RESUMED = 9
    CLIENT_DISCONNECT = 13


class SpeakingState(IntEnum):
    NONE = 0
    VOICE = 1
    SOUNDSHARE = 2
    PRIORITY = 4


class VoiceWebSocket(BaseConnection):
    @property
    def heartbeat_payload(self):
        payload = {
            'op': VoiceConnectionOpcode.HEARTBEAT,
            'd': 0
        }
        return payload

    @property
    def identify_payload(self):
        payload = {
            'op': VoiceConnectionOpcode.IDENTIFY,
            'd': {
                'server_id': self.pusher.voice_state.guild.id,
                'user_id': self.pusher.voice_state.member.user.id,
                'session_id': self.pusher.voice_state.session_id,
                'token': self.pusher.voice_server_update.token
            }
        }
        return payload

    def set_speaking_state(self, state=SpeakingState.VOICE, delay=0):
        payload = {
            'op': VoiceConnectionOpcode.SPEAKING,
            'd': {
                'speaking': state,
                'delay': delay
            }
        }
        self.send_json(payload)

    def select(self, address, port, mode):
        payload = {
            'op': VoiceConnectionOpcode.SELECT,
            'd': {
                'protocol': 'udp',
                'data': {
                    'address': address,
                    'port': port,
                    'mode': mode
                }
            }
        }
        self.send_json(payload)

    async def ws_receive(self, response):
        if response.opcode == VoiceConnectionOpcode.HELLO:
            self.send_json(self.identify_payload)
            self.heartbeat_handler.heartbeat_interval = response.data['heartbeat_interval'] / 1000
            self.heartbeat_handler.start()
        elif response.opcode == VoiceConnectionOpcode.HEARTBEAT_ACK:
            self.push_event('heartbeat_ack')
        else:
            self.pusher.push_event(
                'op_' + VoiceConnectionOpcode(response.opcode).name, response.data)


class VoiceDatagramProtocol(asyncio.DatagramProtocol):
    def __init__(self, connection):
        self.connection = connection

    def datagram_received(self, data, endpoint):
        self.connection.push_event('datagram_received', data)
