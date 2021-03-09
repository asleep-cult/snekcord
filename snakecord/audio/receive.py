import asyncio

try:
    import opus
except ImportError:
    opus = None

from . import packets


class AudioReceiver:
    def __init__(self, connection, decoder=None):
        if decoder is None:
            if opus is None:
                raise
            self.decoder = decoder

        self.decoder = opus.OpusDecoder()
        self.connection = connection

    def decrypt(self, packet):
        if self.connection.mode == 'xsalsa20_poly1305':
            nonce = bytearray(24)
            nonce[:12] = packet.header

            data = self.connection.secret_box.decrypt(packet.data, bytes(nonce))
            self.connection.loop.run_in_executor(None, self.decode, data)

    def decode(self, data):
        frames = opus.get_nb_frames(data)
        samples_per_frame = opus.get_samples_per_frame(data)
        channels = opus.get_nb_channels(data)
        print(frames, samples_per_frame, channels)

        decoded = self.decoder.decode(data, frames * samples_per_frame, channels, False)

        asyncio.run_coroutine_threadsafe(self.voice_packet_received(decoded), self.connection.loop)

    async def received(self, datagram):
        packet = packets.RTPHeader.new(datagram)

        tp = packets.RTPHeader.get_payload_type(ord(packet.sbyte))
        if tp != 120:
            return

        self.decrypt(packet)

    async def voice_packet_received(self, data):
        pass
