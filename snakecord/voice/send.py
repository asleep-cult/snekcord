import asyncio
import os
import queue
import subprocess
import threading


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


class FFmpegSubprocess(subprocess.Popen):
    def __init__(self, fmt, path, *args, ffmpeg='ffmpeg', **kwargs):
        self.stdout_read, self.stdout_write = os.pipe()
        super().__init__((
            ffmpeg,
            '-i', path,
            '-f', fmt,
            '-ar', '48000',
            '-ac', '2',
            '-loglevel', '0',
            'pipe:1',
            *args
        ), stdout=self.stdout_write, stdin=subprocess.DEVNULL, **kwargs)


class FFmpegPCMEncoder(FFmpegSubprocess):
    FORMAT = 's16le'

    def __init__(self, *args, **kwargs):
        super(self.FORMAT, *args, **kwargs)


class FFmpegOpusEncoder(FFmpegSubprocess):
    FORMAT = 'opus'

    def __init__(self, *args, **kwargs):
        super().__init__(self.FORMAT, *args, **kwargs)


class AsyncPipeReader(asyncio.StreamReader):
    @classmethod
    async def new(cls, encoder, loop):
        self = cls()
        self.encoder = encoder

        self.pipe = encoder.stdout_read

        self.transport, self.protocol = \
            await loop.connect_read_pipe(self.create_protocol, self.pipe)

        return self

    def create_protocol(self):
        return asyncio.StreamReaderProtocol(self)

    def at_eof(self):
        if self.encoder.poll() is None:
            os.close(self.encoder.stdout_write)
            self.feed_eof()
        return super().at_eof()

    def _check_eof(self):
        if self.at_eof():
            raise EOFError

    def readline(self):
        self._check_eof()
        return super().readline

    def read(self, n):
        self._check_eof()
        return super().read(n)

    def readexactly(self, n):
        self._check_eof()
        return super().readexactly(n)

    def readuntil(self, separator):
        self._check_eof()
        return super().readuntil(separator)


class AudioPlayer:
    @classmethod
    async def new(cls, connection, encoder):
        self = cls()
        self.connection = connection
        self.encoder = encoder
        self.pipe = self.encoder.stdout_read
        self.loop = self.connect.loop
        self.reader = await AsyncPipeReader.new(self.pipe, self.loop)
        return self
