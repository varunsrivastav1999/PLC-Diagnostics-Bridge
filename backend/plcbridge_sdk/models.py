from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.schemas.plc import DataType, PLCType


class ConnectionParams(BaseModel):
    """Library-friendly connection model that supports both built-in and custom PLC types."""

    plc_type: str
    ip: str
    port: Optional[int] = None
    rack: Optional[int] = 0
    slot: Optional[int] = 1
    cpu_type: Optional[str] = None

    model_config = ConfigDict(extra="ignore")

    @field_validator("plc_type", mode="before")
    @classmethod
    def normalize_plc_type(cls, value: PLCType | str) -> str:
        return getattr(value, "value", str(value)).strip().lower()


class ReadParams(ConnectionParams):
    data_type: DataType | str
    address: str
    bit_offset: Optional[int] = 0
    register_count: Optional[int] = 1

    @field_validator("data_type", mode="before")
    @classmethod
    def normalize_data_type(cls, value: DataType | str) -> DataType | str:
        if isinstance(value, DataType):
            return value
        try:
            return DataType(str(value).upper())
        except ValueError:
            return str(value)

    @field_validator("bit_offset", mode="before")
    @classmethod
    def coerce_bit_offset(cls, value):
        if value in (None, ""):
            return 0
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    @field_validator("register_count", mode="before")
    @classmethod
    def coerce_register_count(cls, value):
        if value in (None, ""):
            return 1
        try:
            return max(1, min(int(value), 100))
        except (TypeError, ValueError):
            return 1


class WriteParams(ReadParams):
    value: Any

