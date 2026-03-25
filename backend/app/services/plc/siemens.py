import snap7
import re
from typing import Any
from app.services.plc.base import BasePLCService
from app.schemas.plc import PLCConnectRequest, PLCReadRequest, PLCWriteRequest, DataType
from app.core.exceptions import PLCConnectionError, PLCReadError, PLCWriteError
import logging

logger = logging.getLogger(__name__)


class SiemensPLCService(BasePLCService):
    def __init__(self):
        super().__init__()
        self.client = snap7.client.Client()

    def connect(self, req: PLCConnectRequest) -> bool:
        try:
            rack = req.rack if req.rack is not None else 0
            slot = req.slot if req.slot is not None else 1
            port = req.port if req.port is not None else 102
            # snap7 3.0.0: connect(address, rack, slot, tcp_port=102)
            self.client.connect(req.ip, rack, slot, tcp_port=port)
            self.is_connected = self.client.get_connected()
            return self.is_connected
        except Exception as e:
            self.is_connected = False
            raise PLCConnectionError(f"Siemens connection failed: {e}")

    def disconnect(self) -> bool:
        try:
            if self.is_connected:
                self.client.disconnect()
                self.is_connected = False
        except Exception:
            self.is_connected = False
        return True

    def test_connection(self) -> bool:
        try:
            return self.is_connected and self.client.get_connected()
        except Exception:
            self.is_connected = False
            return False

    def _parse_address(self, address: str):
        """Parse Siemens DB address: DB1.DBX0.0, DB1.DBW2, DB1.DBD4"""
        match = re.match(r"DB(\d+)\.DB([XWBDP])(\d+)(?:\.(\d+))?", address.upper())
        if not match:
            raise ValueError(f"Invalid Siemens DB address: {address}. Use 'DB1.DBX0.0' or 'DB1.DBW2'")
        db_number = int(match.group(1))
        data_type_char = match.group(2)
        start_byte = int(match.group(3))
        bit_offset = int(match.group(4)) if match.group(4) else 0
        return db_number, data_type_char, start_byte, bit_offset

    def read(self, req: PLCReadRequest) -> Any:
        try:
            db_number, dt_char, start, bit_offset = self._parse_address(req.address)

            if req.data_type == DataType.BOOL:
                data = self.client.db_read(db_number, start, 1)
                target_bit = req.bit_offset if req.bit_offset is not None and req.bit_offset > 0 else bit_offset
                return snap7.util.get_bool(data, 0, target_bit)

            elif req.data_type == DataType.INT:
                data = self.client.db_read(db_number, start, 2)
                return snap7.util.get_int(data, 0)

            elif req.data_type == DataType.DINT:
                data = self.client.db_read(db_number, start, 4)
                return snap7.util.get_dint(data, 0)

            elif req.data_type in (DataType.REAL, DataType.FLOAT):
                data = self.client.db_read(db_number, start, 4)
                return round(snap7.util.get_real(data, 0), 6)

            elif req.data_type == DataType.STRING:
                # S7 string: byte 0 = max length, byte 1 = actual length, bytes 2+ = chars
                # Read header first to get actual length
                header = self.client.db_read(db_number, start, 2)
                # max_len = header[0]
                actual_len = header[1]
                if actual_len > 0:
                    data = self.client.db_read(db_number, start, 2 + actual_len)
                    return data[2:2 + actual_len].decode('ascii', errors='replace')
                return ""

            else:
                raise ValueError(f"Unsupported data type: {req.data_type}")

        except Exception as e:
            raise PLCReadError(f"Siemens read failed: {e}")

    def write(self, req: PLCWriteRequest) -> bool:
        try:
            db_number, dt_char, start, bit_offset = self._parse_address(req.address)

            if req.data_type == DataType.BOOL:
                # Read-modify-write for bit safety
                data = bytearray(self.client.db_read(db_number, start, 1))
                target_bit = req.bit_offset if req.bit_offset is not None and req.bit_offset > 0 else bit_offset
                snap7.util.set_bool(data, 0, target_bit, bool(req.value))
                self.client.db_write(db_number, start, data)

            elif req.data_type == DataType.INT:
                data = bytearray(2)
                snap7.util.set_int(data, 0, int(req.value))
                self.client.db_write(db_number, start, data)

            elif req.data_type == DataType.DINT:
                data = bytearray(4)
                snap7.util.set_dint(data, 0, int(req.value))
                self.client.db_write(db_number, start, data)

            elif req.data_type in (DataType.REAL, DataType.FLOAT):
                data = bytearray(4)
                snap7.util.set_real(data, 0, float(req.value))
                self.client.db_write(db_number, start, data)

            elif req.data_type == DataType.STRING:
                # S7 string format: [max_len][actual_len][chars...]
                text = str(req.value)
                max_len = 254
                actual_len = min(len(text), max_len)
                data = bytearray(2 + max_len)
                data[0] = max_len
                data[1] = actual_len
                data[2:2 + actual_len] = text[:actual_len].encode('ascii', errors='replace')
                self.client.db_write(db_number, start, data)

            return True
        except Exception as e:
            raise PLCWriteError(f"Siemens write failed: {e}")
