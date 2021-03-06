import asyncio
import queue
import struct
import subprocess
import threading
import time


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
        self._start = asyncio.Event()
        self.sequence = 0
        self.timestamp = 0

    def make_header(self):
        header = bytearray(12)

        header[0] = 0x80
        header[1] = 0x78
        struct.pack_into(
            '>HII', header, 2,
            self.sequence, self.timestamp, self.connection.ssrc
        )
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

    async def start(self):
        await self.connection.ws.send_speaking()

        start = time.perf_counter()
        i = 0

        async for packet in self.stream:
            i += 1

            data = self.encrypt(packet)
            self.connection.transport.sendto(data)

            delay = self.DELAY + ((start + self.DELAY * i) - time.perf_counter())
            await asyncio.sleep(delay)

            self.increment()

        print('Done')
