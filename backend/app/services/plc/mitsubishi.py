import struct
import pymcprotocol
from typing import Any
from app.services.plc.base import BasePLCService
from app.schemas.plc import PLCConnectRequest, PLCReadRequest, PLCWriteRequest, DataType
from app.core.exceptions import PLCConnectionError, PLCReadError, PLCWriteError

class MitsubishiPLCService(BasePLCService):
    """
    Mitsubishi PLC Service using MC Protocol (MELSEC Communication Protocol).
    Compatible with Q Series, L Series, and FX Series (including FX5U-500B).
    Uses Type3E Ethernet protocol for reliable industrial communication.
    """
    def __init__(self):
        super().__init__()
        self.client = pymcprotocol.Type3E()

    def connect(self, req: PLCConnectRequest) -> bool:
        try:
            port = req.port if req.port is not None else 5000
            self.client.connect(req.ip, port)
            self.is_connected = True
            return True
        except Exception as e:
            self.is_connected = False
            raise PLCConnectionError(f"Mitsubishi connection failed: {e}")

    def disconnect(self) -> bool:
        try:
            self.client.close()
            self.is_connected = False
            return True
        except Exception:
            return False

    def test_connection(self) -> bool:
        return self.is_connected

    def _words_to_bytes(self, words: list[int]) -> bytes:
        """Convert list of 16-bit word values to bytes (little-endian per word)."""
        result = bytearray()
        for w in words:
            result.extend(struct.pack('<H', w & 0xFFFF))
        return bytes(result)

    def _bytes_to_words(self, data: bytes) -> list[int]:
        """Convert bytes to list of 16-bit word values."""
        # Pad to even length
        if len(data) % 2 != 0:
            data = data + b'\x00'
        words = []
        for i in range(0, len(data), 2):
            words.append(struct.unpack('<H', data[i:i+2])[0])
        return words

    def read(self, req: PLCReadRequest) -> Any:
        try:
            headdevice = req.address

            if req.data_type == DataType.BOOL:
                bit_data = self.client.batchread_bitunits(headdevice, 1)
                return bool(bit_data[0]) if bit_data else False

            elif req.data_type == DataType.INT:
                word_data = self.client.batchread_wordunits(headdevice, 1)
                val = word_data[0] if word_data else 0
                # Sign-extend 16-bit to signed int
                if val > 32767:
                    val -= 65536
                return val

            elif req.data_type == DataType.DINT:
                # 32-bit integer = 2 consecutive D registers
                word_data = self.client.batchread_wordunits(headdevice, 2)
                if len(word_data) >= 2:
                    raw = self._words_to_bytes(word_data[:2])
                    return struct.unpack('<i', raw)[0]
                return 0

            elif req.data_type in (DataType.REAL, DataType.FLOAT):
                # 32-bit float = 2 consecutive D registers
                word_data = self.client.batchread_wordunits(headdevice, 2)
                if len(word_data) >= 2:
                    raw = self._words_to_bytes(word_data[:2])
                    return round(struct.unpack('<f', raw)[0], 6)
                return 0.0

            elif req.data_type == DataType.STRING:
                # STRING: each D register holds 2 ASCII characters
                # register_count default is 10 (= 20 chars) for Mitsubishi
                reg_count = getattr(req, 'register_count', 10) or 10
                word_data = self.client.batchread_wordunits(headdevice, reg_count)
                raw = self._words_to_bytes(word_data)
                # Decode as ASCII, strip null terminators and padding
                text = raw.decode('ascii', errors='replace').rstrip('\x00').rstrip()
                return text

            else:
                word_data = self.client.batchread_wordunits(headdevice, 1)
                return word_data[0] if word_data else 0

        except Exception as e:
            raise PLCReadError(f"Mitsubishi read failed: {e}")

    def write(self, req: PLCWriteRequest) -> bool:
        try:
            headdevice = req.address

            if req.data_type == DataType.BOOL:
                self.client.batchwrite_bitunits(headdevice, [int(bool(req.value))])

            elif req.data_type == DataType.INT:
                val = int(req.value) & 0xFFFF
                self.client.batchwrite_wordunits(headdevice, [val])

            elif req.data_type == DataType.DINT:
                raw = struct.pack('<i', int(req.value))
                words = self._bytes_to_words(raw)
                self.client.batchwrite_wordunits(headdevice, words)

            elif req.data_type in (DataType.REAL, DataType.FLOAT):
                raw = struct.pack('<f', float(req.value))
                words = self._bytes_to_words(raw)
                self.client.batchwrite_wordunits(headdevice, words)

            elif req.data_type == DataType.STRING:
                # STRING write: encode to ASCII, pad to fill register_count * 2 bytes
                reg_count = getattr(req, 'register_count', 10) or 10
                text = str(req.value)
                byte_len = reg_count * 2
                encoded = text.encode('ascii', errors='replace')[:byte_len]
                # Pad with null bytes to fill all registers
                encoded = encoded.ljust(byte_len, b'\x00')
                words = self._bytes_to_words(encoded)
                self.client.batchwrite_wordunits(headdevice, words)

            else:
                self.client.batchwrite_wordunits(headdevice, [int(req.value)])

            return True
        except Exception as e:
            raise PLCWriteError(f"Mitsubishi write failed: {e}")
