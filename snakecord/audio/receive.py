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

            return self.connection.secret_box.decrypt(packet.data, bytes(nonce))

    def decode(self, data):
        decoded = self.decoder.decode(data, opus.MAX_FRAME_SIZE, opus.CHANNELS, False)

        asyncio.run_coroutine_threadsafe(self.voice_packet_received(decoded), self.connection.loop)

    async def received(self, datagram):
        packet = packets.RTPHeader.new(datagram)

        tp = packets.RTPHeader.get_payload_type(ord(packet.sbyte))
        if tp != packets.RTPHeader.TYPE:
            return

        data = self.decrypt(packet)

        if packets.RTPHeader.has_extension(ord(packet.fbyte)):
            packet.extension, data = packets.RTPHeaderExtension.new(data)

        self.connection.loop.run_in_executor(None, self.decode, data)

    async def voice_packet_received(self, data):
        pass
