import asyncio
import queue
import threading

try:
    import opus
except ImportError:
    opus = None

SILENCE = b'\xF8\xFF\xFE'
SAMPLES_PER_FRAME = 960
FRAME_SIZE = SAMPLES_PER_FRAME * 4


class WorkerThread(threading.Thread):
    EXIT = object()

    def __init__(self, daemon=False):
        threading.Thread.__init__(self, daemon=daemon)
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


class OggPage:
    DURATION = 0.02
    LENGTH = 27
    PREFIX = b'OggS'

    class Sentinel(Exception):
        pass

    @classmethod
    async def new(cls, reader):
        self = cls()

        while True:
            try:
                prefix = await reader.readexactly(len(self.PREFIX))
            except EOFError:
                raise cls.Sentinel

            if prefix == self.PREFIX:
                break

        data = await reader.readexactly(self.LENGTH - len(self.PREFIX))

        self.version = data[4]
        self.type = data[5]

        self.granule_position = int.from_bytes(data[6:10], 'little', signed=False)
        self.bitstream_serial_number = int.from_bytes(data[10:14], 'little', signed=False)
        self.page_serial_number = int.from_bytes(data[14:18], 'little', signed=False)
        self.crc_checksum = int.from_bytes(data[18:22], 'little', signed=False)

        self.page_segments = data[26]

        self.segment_table = await reader.readexactly(self.page_segments)
        self.data = await reader.readexactly(sum(self.segment_table))

        return self


async def get_packets(reader):
    pending = b''

    while True:
        try:
            page = await OggPage.new(reader)
        except OggPage.Sentinel:
            for _ in range(5):
                yield SILENCE
            return

        packet_start = 0
        packet_end = 0

        for segment in page.segment_table:
            packet_end += segment

            pending += page.data[packet_start:packet_end]

            if segment != 0xFF:
                yield pending
                pending = b''

            packet_start = packet_end


async def get_packets_encoded(reader, loop, encoder=None):
    if encoder is None:
        if opus is None:
            raise Exception

        encoder = opus.OpusEncoder()

    def do_encode():
        coro = reader.read(FRAME_SIZE)
        future = asyncio.run_coroutine_threadsafe(coro, loop)

        try:
            packet = future.result()
        except EOFError:
            worker.close()
            return worker.EXIT

        worker.put(do_encode)

        return encoder.encode(packet, SAMPLES_PER_FRAME)

    worker = WorkerThread()
    worker.put(do_encode)
    worker.start()

    while True:
        result = await worker.out_queue.get()

        if result is worker.EXIT:
            for _ in range(5):
                yield SILENCE
            return

        yield result
