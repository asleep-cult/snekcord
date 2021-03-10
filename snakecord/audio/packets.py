import asyncio
import struct

try:
    import opus
except ImportError:
    opus = None

from ..utils import cstruct, undefined


SILENCE = b'\xF8\xFF\xFE'

OPUS_FRAME_DURATION = 0.02
OPUS_SAMPLING_RATE = 48000
OPUS_CHANNELS = 2
OPUS_SAMPLE_SIZE = cstruct.Short.size * OPUS_CHANNELS
OPUS_SAMPLES_PER_FRAME = int(OPUS_SAMPLING_RATE * OPUS_FRAME_DURATION)
OPUS_FRAME_SIZE = OPUS_SAMPLE_SIZE * OPUS_SAMPLES_PER_FRAME


class RTPHeader(cstruct):
    TYPE = 120

    byteorder = '>'
    fbyte: cstruct.Char
    sbyte: cstruct.Char
    sequence: cstruct.UnsignedShort
    timestamp: cstruct.UnsignedInt
    ssrc: cstruct.UnsignedInt

    @staticmethod
    def get_version(byte):
        return byte & 0b11000000

    @staticmethod
    def get_padding(byte):
        return byte & 0b00100000

    @staticmethod
    def has_extension(byte):
        return byte & 0b00010000

    @staticmethod
    def get_csrc_count(byte):
        return byte & 0b00001111

    @staticmethod
    def get_marker(byte):
        return byte & 0b10000000

    @staticmethod
    def get_payload_type(byte):
        return byte & 0b01111111

    @classmethod
    def new(cls, data):
        self = cls.unpack_from(data)
        self.extension = None
        self.header = data[:cls.struct.size]

        self.csrc_list = []
        csrc_count = min((cls.get_csrc_count(ord(self.fbyte)), 15))
        if csrc_count:
            fmt = '>{}I'.format(csrc_count)
            self.csrc_list.extend(struct.unpack_from(fmt, data, cls.struct.size))

        offset = cls.struct.size + cstruct.UnsignedInt.size * csrc_count
        self.data = data[offset:]

        return self


class RTPHeaderExtension(cstruct):
    byteorder = '>'
    profile: cstruct.UnsignedShort
    length: cstruct.UnsignedShort

    @classmethod
    def new(cls, data):
        self = cls.unpack_from(data)

        fmt = '>{}I'.format(self.length)
        self.data = struct.unpack_from(fmt, data, cls.struct.size)

        offset = cls.struct.size + self.length * cstruct.UnsignedInt.size
        return self, data[offset:]


class OggPage(cstruct):
    PREFIX = b'OggS'

    byteorder = '<'
    version: cstruct.UnsignedChar
    header_type: cstruct.UnsignedChar
    granule_position: cstruct.UnsignedLongLong
    bitstream_serial_number: cstruct.UnsignedLong
    page_sequence_number: cstruct.UnsignedLong
    crc_checksum: cstruct.UnsignedLong
    page_segments: cstruct.UnsignedChar

    @classmethod
    async def new(cls, reader):
        self = cls.unpack(await reader.readexactly(cls.struct.size))
        self.segment_table = await reader.readexactly(self.page_segments)
        self.data = await reader.readexactly(sum(self.segment_table))
        return self


async def get_packets(reader):
    pending = b''

    while True:
        try:
            prefix = await reader.readexactly(len(OggPage.PREFIX))
        except asyncio.IncompleteReadError:
            return

        if prefix != OggPage.PREFIX:
            continue

        packet_start = packet_end = 0

        page = await OggPage.new(reader)

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

    queue = asyncio.Queue()

    def do_encode():
        coro = reader.read(OPUS_FRAME_SIZE)
        future = asyncio.run_coroutine_threadsafe(coro, loop)

        try:
            packet = future.result()
        except asyncio.IncompleteReadError:
            queue.put_nowait(undefined)
            return

        if len(packet) != OPUS_FRAME_SIZE:
            queue.put_nowait(undefined)
            return

        encoded = encoder.encode(packet, OPUS_SAMPLES_PER_FRAME)
        queue.put_nowait(encoded)

        loop.run_in_executor(None, do_encode)

    loop.run_in_executor(None, do_encode)

    while True:
        item = await queue.get()

        if item is undefined:
            return

        yield item
