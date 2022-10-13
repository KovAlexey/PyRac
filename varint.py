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


