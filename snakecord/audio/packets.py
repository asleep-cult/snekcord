SILENCE = b'\xF8\xFF\xFE'


class Sentinel(Exception):
    ...


class OggPage:
    LENGTH = 27

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
                yield SILENCE
            return

        packet_start = 0
        packet_end = 0

        for segment in page.segment_table:
            packet_end += segment

            if segment == 0xFF:
                pending += page.data[packet_start:packet_end]
            else:
                pending += page.data[packet_start:packet_end]
                yield pending
                pending = b''

            packet_start = packet_end
