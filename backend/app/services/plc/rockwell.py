from pylogix import PLC
from typing import Any
from app.services.plc.base import BasePLCService
from app.schemas.plc import PLCConnectRequest, PLCReadRequest, PLCWriteRequest, DataType
from app.core.exceptions import PLCConnectionError, PLCReadError, PLCWriteError
import logging

logger = logging.getLogger(__name__)


class RockwellPLCService(BasePLCService):
    def __init__(self):
        super().__init__()
        self.client = PLC()

    def connect(self, req: PLCConnectRequest) -> bool:
        try:
            self.client.IPAddress = req.ip
            if req.port is not None:
                self.client.Port = req.port
            if req.slot is not None:
                self.client.ProcessorSlot = req.slot

            # Verify by reading PLC time
            ret = self.client.GetPLCTime()
            if ret.Status == 'Success':
                self.is_connected = True
                logger.info(f"Rockwell connected: {req.ip}:{req.port} slot={req.slot}")
                return True
            else:
                raise PLCConnectionError(f"Rockwell connection failed: {ret.Status}")
        except PLCConnectionError:
            raise
        except Exception as e:
            self.is_connected = False
            raise PLCConnectionError(f"Rockwell connection failed: {e}")

    def disconnect(self) -> bool:
        try:
            self.client.Close()
        except Exception:
            pass
        self.is_connected = False
        return True

    def test_connection(self) -> bool:
        if not self.is_connected:
            return False
        try:
            ret = self.client.GetPLCTime()
            return ret.Status == 'Success'
        except Exception:
            self.is_connected = False
            return False

    def read(self, req: PLCReadRequest) -> Any:
        try:
            ret = self.client.Read(req.address)
            if ret.Status != 'Success':
                raise PLCReadError(f"Rockwell read failed: {ret.Status}")
            val = ret.Value

            # Type-coerce based on data_type
            if req.data_type == DataType.BOOL:
                return bool(val)
            elif req.data_type in (DataType.INT, DataType.DINT):
                return int(val) if val is not None else 0
            elif req.data_type in (DataType.REAL, DataType.FLOAT):
                return round(float(val), 6) if val is not None else 0.0
            elif req.data_type == DataType.STRING:
                return str(val) if val is not None else ""
            return val
        except PLCReadError:
            raise
        except Exception as e:
            raise PLCReadError(f"Rockwell read failed: {e}")

    def write(self, req: PLCWriteRequest) -> bool:
        try:
            # Coerce value to correct Python type
            val = req.value
            if req.data_type == DataType.BOOL:
                val = bool(str(val).lower() in ['true', '1', 't', 'yes'])
            elif req.data_type in (DataType.INT, DataType.DINT):
                val = int(val)
            elif req.data_type in (DataType.REAL, DataType.FLOAT):
                val = float(val)
            elif req.data_type == DataType.STRING:
                val = str(val)

            ret = self.client.Write(req.address, val)
            if ret.Status != 'Success':
                raise PLCWriteError(f"Rockwell write failed: {ret.Status}")
            return True
        except PLCWriteError:
            raise
        except Exception as e:
            raise PLCWriteError(f"Rockwell write failed: {e}")
