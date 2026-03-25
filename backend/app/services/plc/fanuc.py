from typing import Any
from app.services.plc.base import BasePLCService
from app.schemas.plc import PLCConnectRequest, PLCReadRequest, PLCWriteRequest, DataType
from app.core.exceptions import PLCConnectionError, PLCReadError, PLCWriteError

class FanucPLCService(BasePLCService):
    """
    Mock implementation for Fanuc as native TCP python wrappers for proprietary SNPX/GE logic
    are highly specialized. This structure mimics expected interactions.
    """
    def __init__(self):
        super().__init__()
        self.mock_store = {}

    def connect(self, req: PLCConnectRequest) -> bool:
        self.is_connected = True
        return True

    def disconnect(self) -> bool:
        self.is_connected = False
        return True

    def test_connection(self) -> bool:
        return self.is_connected

    def read(self, req: PLCReadRequest) -> Any:
        if not self.is_connected:
            raise PLCReadError("Fanuc not connected")
        
        val = self.mock_store.get(req.address)
        if val is not None:
            return val
            
        # Return default if not set
        if req.data_type == DataType.BOOL:
            return False
        elif req.data_type in [DataType.INT, DataType.DINT]:
            return 0
        elif req.data_type in [DataType.REAL, DataType.FLOAT]:
            return 0.0
        elif req.data_type == DataType.STRING:
            return ""
        return 0

    def write(self, req: PLCWriteRequest) -> bool:
        if not self.is_connected:
            raise PLCWriteError("Fanuc not connected")
        
        # Depending on type perform conversion logic
        val = req.value
        if req.data_type == DataType.BOOL:
            val = str(val).lower() in ['true', '1', 't', 'y', 'yes']
        elif req.data_type in [DataType.INT, DataType.DINT]:
            val = int(val)
        elif req.data_type in [DataType.REAL, DataType.FLOAT]:
            val = float(val)
        elif req.data_type == DataType.STRING:
            val = str(val)
            
        self.mock_store[req.address] = val
        return True
