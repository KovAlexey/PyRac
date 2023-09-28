from io import BytesIO
import sys


class varintCodec:
    @staticmethod
    def Encode(number):
        """Pack `number` into varint bytes"""
        buffer = b''
        while True:
            towrite = number & 0x7F
            number >>= 7
            if number:
                buffer += (towrite | 0x80).to_bytes(1, 'big')
            else:
                buffer += towrite.to_bytes(1, 'big')
                break
        return buffer

    @staticmethod
    def DecodeFromStream(stream):
        buffer = 0
        shift = 0
        while True:
            bytes_recv = stream.read(1)
            value = bytes_recv[0] & 0b01111111
            buffer |= (value << shift)
            shift += 7
            if not bytes_recv[0] & 0b10000000:
                break
        return buffer


