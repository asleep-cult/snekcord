import asyncio
import queue
import threading

try:
    import opus
except ImportError:
    opus = None


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


class Sentinel(Exception):
    ...


class OggPage:
    DURATION = 0.02
    LENGTH = 27
    SILENCE = b'\xF8\xFF\xFE'

    @classmethod
    async def new(cls, reader):
        self = cls()

        try:
            data = await reader.readexactly(self.LENGTH)
        except EOFError:
            raise Sentinel

        assert data[:4] == b'OggS'

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
        except Sentinel:
            for _ in range(5):
                yield OggPage.SILENCE
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


async def get_packets_encoded(reader):
    if opus is None:
        raise Exception

    encoder = opus.OpusEncoder()
    encoder.set_bitrate(128)
    encoder.set_fec(True)

    iterator = get_packets(reader)

    def _do_encode():
        coro = iterator.asend(None)
        future = asyncio.run_coroutine_threadsafe(coro, asyncio.get_event_loop())

        try:
            packet = future.result()
        except StopAsyncIteration:
            worker.close()
            return worker.EXIT

        return encoder.encode(packet, 960)

        worker.put(_do_encode)

    worker = WorkerThread()
    worker.put(_do_encode)

    while True:
        result = await worker.out_queue.get()

        if result is worker.EXIT:
            return

        yield result
