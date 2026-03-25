import struct
from pymodbus.client import ModbusTcpClient
from typing import Any
from app.services.plc.base import BasePLCService
from app.schemas.plc import PLCConnectRequest, PLCReadRequest, PLCWriteRequest, DataType
from app.core.exceptions import PLCConnectionError, PLCReadError, PLCWriteError
import logging

logger = logging.getLogger(__name__)


class ABBPLCService(BasePLCService):
    """ABB / Generic Modbus TCP adapter using pymodbus 3.x API."""

    def __init__(self):
        super().__init__()
        self.client = None

    def connect(self, req: PLCConnectRequest) -> bool:
        try:
            port = req.port if req.port is not None else 502
            self.client = ModbusTcpClient(req.ip, port=port, timeout=5)
            self.is_connected = self.client.connect()
            if not self.is_connected:
                raise PLCConnectionError("ABB Modbus connection rejected")
            logger.info(f"ABB Modbus connected: {req.ip}:{port}")
            return True
        except PLCConnectionError:
            raise
        except Exception as e:
            self.is_connected = False
            raise PLCConnectionError(f"ABB connection failed: {e}")

    def disconnect(self) -> bool:
        try:
            if self.client:
                self.client.close()
        except Exception:
            pass
        self.is_connected = False
        return True

    def test_connection(self) -> bool:
        try:
            return self.is_connected and self.client is not None and self.client.is_socket_open()
        except Exception:
            self.is_connected = False
            return False

    def _parse_address(self, address: str) -> int:
        try:
            val = int(address)
            # Holding registers (4xxxx)
            if 40000 <= val < 50000:
                return val - 40001
            # Input registers (3xxxx)
            elif 30000 <= val < 40000:
                return val - 30001
            # Coils (0xxxx)
            elif 1 <= val < 10000:
                return val - 1
            return val
        except ValueError:
            raise ValueError("ABB/Modbus requires integer addresses (e.g., '40001' or '00001')")

    def _is_coil_address(self, address: str) -> bool:
        try:
            return int(address) < 10000
        except ValueError:
            return False

    def read(self, req: PLCReadRequest) -> Any:
        try:
            addr = self._parse_address(req.address)
            slave_id = 1

            if req.data_type == DataType.BOOL:
                if self._is_coil_address(req.address):
                    rr = self.client.read_coils(addr, 1, slave=slave_id)
                    if rr.isError():
                        raise PLCReadError(f"Modbus coil read error: {rr}")
                    return bool(rr.bits[0])
                else:
                    rr = self.client.read_holding_registers(addr, 1, slave=slave_id)
                    if rr.isError():
                        raise PLCReadError(f"Modbus register read error: {rr}")
                    target_bit = req.bit_offset if req.bit_offset is not None else 0
                    return bool((rr.registers[0] >> target_bit) & 1)

            elif req.data_type == DataType.INT:
                rr = self.client.read_holding_registers(addr, 1, slave=slave_id)
                if rr.isError():
                    raise PLCReadError(f"Modbus read error: {rr}")
                val = rr.registers[0]
                # Sign-extend 16-bit
                if val > 32767:
                    val -= 65536
                return val

            elif req.data_type == DataType.DINT:
                # 32-bit = 2 consecutive registers
                rr = self.client.read_holding_registers(addr, 2, slave=slave_id)
                if rr.isError():
                    raise PLCReadError(f"Modbus read error: {rr}")
                raw = struct.pack('>HH', rr.registers[0], rr.registers[1])
                return struct.unpack('>i', raw)[0]

            elif req.data_type in (DataType.REAL, DataType.FLOAT):
                # 32-bit float = 2 consecutive registers
                rr = self.client.read_holding_registers(addr, 2, slave=slave_id)
                if rr.isError():
                    raise PLCReadError(f"Modbus read error: {rr}")
                raw = struct.pack('>HH', rr.registers[0], rr.registers[1])
                return round(struct.unpack('>f', raw)[0], 6)

            elif req.data_type == DataType.STRING:
                reg_count = getattr(req, 'register_count', 10) or 10
                rr = self.client.read_holding_registers(addr, reg_count, slave=slave_id)
                if rr.isError():
                    raise PLCReadError(f"Modbus read error: {rr}")
                raw = b''
                for r in rr.registers:
                    raw += struct.pack('>H', r)
                return raw.decode('ascii', errors='replace').rstrip('\x00').rstrip()

            else:
                rr = self.client.read_holding_registers(addr, 1, slave=slave_id)
                if rr.isError():
                    raise PLCReadError(f"Modbus read error: {rr}")
                return rr.registers[0]

        except PLCReadError:
            raise
        except Exception as e:
            raise PLCReadError(f"ABB read failed: {e}")

    def write(self, req: PLCWriteRequest) -> bool:
        try:
            addr = self._parse_address(req.address)
            slave_id = 1

            if req.data_type == DataType.BOOL:
                if self._is_coil_address(req.address):
                    val = str(req.value).lower() in ['true', '1', 't', 'yes']
                    wr = self.client.write_coil(addr, val, slave=slave_id)
                else:
                    wr = self.client.write_register(addr, int(bool(req.value)), slave=slave_id)

            elif req.data_type == DataType.INT:
                val = int(req.value) & 0xFFFF
                wr = self.client.write_register(addr, val, slave=slave_id)

            elif req.data_type == DataType.DINT:
                raw = struct.pack('>i', int(req.value))
                hi, lo = struct.unpack('>HH', raw)
                wr = self.client.write_registers(addr, [hi, lo], slave=slave_id)

            elif req.data_type in (DataType.REAL, DataType.FLOAT):
                raw = struct.pack('>f', float(req.value))
                hi, lo = struct.unpack('>HH', raw)
                wr = self.client.write_registers(addr, [hi, lo], slave=slave_id)

            elif req.data_type == DataType.STRING:
                reg_count = getattr(req, 'register_count', 10) or 10
                text = str(req.value)
                byte_len = reg_count * 2
                encoded = text.encode('ascii', errors='replace')[:byte_len].ljust(byte_len, b'\x00')
                words = []
                for i in range(0, len(encoded), 2):
                    words.append(struct.unpack('>H', encoded[i:i + 2])[0])
                wr = self.client.write_registers(addr, words, slave=slave_id)

            else:
                wr = self.client.write_register(addr, int(req.value), slave=slave_id)

            if wr.isError():
                raise PLCWriteError(f"Modbus write error: {wr}")
            return True

        except PLCWriteError:
            raise
        except Exception as e:
            raise PLCWriteError(f"ABB write failed: {e}")
