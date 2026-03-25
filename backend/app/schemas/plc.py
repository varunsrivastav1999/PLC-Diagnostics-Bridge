from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, Any
from enum import Enum

class PLCType(str, Enum):
    siemens = "siemens"
    mitsubishi = "mitsubishi"
    rockwell = "rockwell"
    abb = "abb"
    fanuc = "fanuc"

class OperationType(str, Enum):
    read = "read"
    write = "write"

class DataType(str, Enum):
    BOOL = "BOOL"
    INT = "INT"
    DINT = "DINT"
    REAL = "REAL"
    FLOAT = "FLOAT"
    STRING = "STRING"

class PLCConnectRequest(BaseModel):
    plc_type: PLCType
    ip: str
    port: Optional[int] = None
    rack: Optional[int] = 0
    slot: Optional[int] = 1
    cpu_type: Optional[str] = None
    
    model_config = ConfigDict(extra='ignore')

class PLCReadRequest(BaseModel):
    plc_type: PLCType
    ip: str
    port: Optional[int] = None
    rack: Optional[int] = 0
    slot: Optional[int] = 1
    data_type: DataType
    address: str
    bit_offset: Optional[int] = 0
    register_count: Optional[int] = 1

    model_config = ConfigDict(extra='ignore')

    @field_validator('bit_offset', mode='before')
    @classmethod
    def coerce_bit_offset(cls, v):
        if v is None or v == '':
            return 0
        try:
            return int(v)
        except (ValueError, TypeError):
            return 0

    @field_validator('register_count', mode='before')
    @classmethod
    def coerce_register_count(cls, v):
        if v is None or v == '':
            return 1
        try:
            val = int(v)
            return max(1, min(val, 100))
        except (ValueError, TypeError):
            return 1

class PLCWriteRequest(PLCReadRequest):
    value: Any
    
class PLCStatusRequest(BaseModel):
    plc_type: PLCType
    ip: str

