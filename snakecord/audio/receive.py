import nacl

from . import packets


class AudioReceiver:
    def __init__(self, connection):
        self.connection = connection

    def decrypt(self, data):
        if self.connection.mode == 'xsalsa20_poly1305':
            nonce = bytearray(24)
            nonce[:12] = data[:12]

            return self.connection.secret_box.decrypt(data, bytes(nonce))

    async def received(self, data):
        size = packets.RTPHeader.struct.size
        header = packets.RTPHeader.unpack(data[:size])
        # decrypted = self.decrypt(data[size:])
        print(packets.RTPHeader.get_payload_type(ord(header.sbyte)))
        # print(header.values, decrypted)
