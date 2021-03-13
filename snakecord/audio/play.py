import asyncio
import subprocess
import time

from . import packets


class FFmpegSubprocess:
    @classmethod
    async def new(cls, fmt, path, *args, ffmpeg='ffmpeg', **kwargs):
        self = cls()
        self.proc = await asyncio.create_subprocess_exec(
            ffmpeg,
            '-i', path,
            '-f', fmt,
            '-ar', '48000',
            '-ac', '2',
            '-loglevel', '0',
            'pipe:1',
            *args,
            stdout=subprocess.PIPE
        )
        return self


class FFmpegPCMEncoder(FFmpegSubprocess):
    FORMAT = 's16le'

    @classmethod
    def new(cls, *args, **kwargs):
        return FFmpegSubprocess.new(cls.FORMAT, *args, **kwargs)


class FFmpegOpusEncoder(FFmpegSubprocess):
    FORMAT = 'opus'

    @classmethod
    def new(cls, *args, **kwargs):
        return FFmpegSubprocess.new(cls.FORMAT, *args, **kwargs)


class AudioPlayer:
    MAX_SEQUENCE = 0xFFFF
    MAX_TIMESTAMP = 0xFFFFFFFF

    def __init__(self, connection, stream):
        self.connection = connection
        self.stream = stream
        self._start_playing = asyncio.Event()
        self.sequence = 0
        self.timestamp = 0
        self.page_index = 0
        self.started_at = 0

    def make_header(self):
        return packets.RTPHeader.pack(
            fbyte=b'\x80', sbyte=b'\x78',
            sequence=self.sequence,
            timestamp=self.timestamp,
            ssrc=self.connection.ssrc
        )

    def encrypt(self, data):
        header = self.make_header()

        if self.connection.mode == 'xsalsa20_poly1305':
            nonce = bytearray(24)
            nonce[:12] = header

            encrypted = self.connection.secret_box.encrypt(bytes(data), bytes(nonce))

            return header + encrypted.ciphertext

    def increment(self):
        self.sequence += 1
        self.timestamp += packets.OPUS_SAMPLES_PER_FRAME

        if self.sequence > self.MAX_SEQUENCE:
            self.sequence = 0

        if self.timestamp > self.MAX_TIMESTAMP:
            self.timestamp = 0

        self.page_index += 1

    def send_packet(self, packet):
        data = self.encrypt(packet)
        self.connection.transport.sendto(data)
        self.increment()

    async def wait(self):
        expected_time = self.started_at + self.expected_elapsed
        offset = expected_time - time.perf_counter()
        delay = offset + packets.OPUS_FRAME_DURATION
        await asyncio.sleep(delay)

    async def start(self, *, wait=True):
        await self.connection.ws.send_speaking()

        self.started_at = time.perf_counter()

        async for packet in self.stream:
            self.send_packet(packet)

            if wait:
                await self.wait()

    @property
    def expected_elapsed(self):
        return packets.OPUS_FRAME_DURATION * self.page_index

    @property
    def elapsed(self):
        return time.perf_counter() - self.started_at
