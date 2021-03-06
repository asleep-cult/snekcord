import asyncio
import queue
import subprocess
import threading
import time

from .packets import OggPage


class WorkerThread(threading.Thread):
    EXIT = object()

    def __init__(self, daemon=False):
        super().__init__(daemon=daemon)
        self.in_queue = queue.Queue()
        self.out_queue = asyncio.Queue()
        self.working = False

    def put(self, func, *args, **kwargs):
        self.in_queue.put_nowait((func, args, kwargs))

    def close(self):
        self.in_queue.put_nowait(self.EXIT)

    def run(self):
        while True:
            todo = self.in_queue.get()
            if todo is self.EXIT:
                return
            func, args, kwargs = todo
            self.working = True
            result = func(*args, **kwargs)
            self.working = False
            self.out_queue.put_nowait(result)


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
    def new(self, *args, **kwargs):
        return FFmpegSubprocess.new(self.FORMAT, *args, **kwargs)


class FFmpegOpusEncoder(FFmpegSubprocess):
    FORMAT = 'opus'

    @classmethod
    def new(self, *args, **kwargs):
        return FFmpegSubprocess.new(self.FORMAT, *args, **kwargs)


class AudioPlayer:
    DELAY = 0.02

    def __init__(self, connection, stream):
        self.connection = connection
        self.stream = stream
        self._start_playing = asyncio.Event()
        self.sequence = 0
        self.timestamp = 0
        self.page_index = 0
        self.started_at = 0
        self.connection.player = self

    def make_header(self):
        header = bytearray(12)

        header[0] = 0x80
        header[1] = 0x78
        header[2:4] = self.sequence.to_bytes(2, 'big', signed=False)
        header[4:8] = self.timestamp.to_bytes(4, 'big', signed=False)
        header[8:12] = self.connection.ssrc.to_bytes(4, 'big', signed=False)

        return header

    def encrypt(self, data):
        header = self.make_header()

        if self.connection.mode == 'xsalsa20_poly1305':
            nonce = bytearray(24)
            nonce[:12] = header

            encrypted = self.connection.secret_box.encrypt(bytes(data), bytes(nonce))

            return header + encrypted.ciphertext

    def increment(self):
        self.sequence += 1
        self.timestamp += (48000 // 100) * 2

        if self.sequence >= 2 ** 16:
            self.sequence = 0

        if self.timestamp >= 2 ** 32:
            self.timestamp = 0

        self.page_index += 1

    async def start(self):
        await self.connection.ws.send_speaking()

        self.started_at = time.perf_counter()

        async for packet in self.stream:
            await self._start_playing.wait()

            data = self.encrypt(packet)
            self.connection.transport.sendto(data)

            expected_time = self.started_at + self.expected_elapsed
            offset = expected_time - time.perf_counter()
            delay = offset + OggPage.DURATION
            await asyncio.sleep(delay)

            self.increment()

    @property
    def expected_elapsed(self):
        return OggPage.DURATION * self.page_index

    @property
    def elapsed(self):
        return time.perf_counter() - self.started_at
