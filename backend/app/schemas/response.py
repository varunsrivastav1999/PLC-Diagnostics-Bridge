from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime

class PLCResponse(BaseModel):
    success: bool
    message: str
    value: Optional[Any] = None
    connected: bool
    timestamp: Optional[datetime] = None
    plc_type: Optional[str] = None
    address: Optional[str] = None
