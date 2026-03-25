from abc import ABC, abstractmethod
from typing import Any
from app.schemas.plc import PLCConnectRequest, PLCReadRequest, PLCWriteRequest, DataType

class BasePLCService(ABC):
    def __init__(self):
        self.is_connected = False

    @abstractmethod
    def connect(self, req: PLCConnectRequest) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        pass

    @abstractmethod
    def read(self, req: PLCReadRequest) -> Any:
        pass

    @abstractmethod
    def write(self, req: PLCWriteRequest) -> bool:
        pass
