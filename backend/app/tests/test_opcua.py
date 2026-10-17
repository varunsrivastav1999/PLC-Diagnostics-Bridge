import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.schemas.plc import DataType, PLCConnectRequest, PLCReadRequest, PLCWriteRequest
from app.services.plc.factory import get_plc_service
from app.services.plc.opcua import OPCUAPLCService


def test_opcua_service_factory_resolution():
    service = get_plc_service("opcua")
    assert isinstance(service, OPCUAPLCService)
    assert service.is_connected is False


def test_opcua_url_building():
    service = OPCUAPLCService()
    # Host without prefix
    assert service._build_endpoint_url("192.168.1.50", 4840) == "opc.tcp://192.168.1.50:4840"
    # Host with default port None
    assert service._build_endpoint_url("10.0.0.1", None) == "opc.tcp://10.0.0.1:4840"
    # Custom port
    assert service._build_endpoint_url("10.0.0.1", 4848) == "opc.tcp://10.0.0.1:4848"
    # Already has opc.tcp prefix
    assert service._build_endpoint_url("opc.tcp://myserver:4840/UA", None) == "opc.tcp://myserver:4840/UA"


def test_opcua_mock_connect_read_write():
    service = OPCUAPLCService()
    mock_client = MagicMock()
    mock_node = MagicMock()

    # Setup mock node methods
    mock_node.read_value = AsyncMock(side_effect=[
        True,          # BOOL
        42,            # INT
        100000,        # DINT
        3.14159,       # REAL
        "Hello OPC-UA" # STRING
    ])
    mock_node.write_value = AsyncMock(return_value=None)
    mock_client.get_node.return_value = mock_node

    service.client = mock_client
    service.is_connected = True
    service._start_loop()
    service._start_worker("test-opcua")

    try:
        # 1. Read BOOL
        req_bool = PLCReadRequest(
            plc_type="opcua",
            ip="127.0.0.1",
            data_type=DataType.BOOL,
            address="ns=2;s=Device.Running"
        )
        assert service.read(req_bool) is True

        # 2. Read INT
        req_int = PLCReadRequest(
            plc_type="opcua",
            ip="127.0.0.1",
            data_type=DataType.INT,
            address="ns=2;s=Device.RPM"
        )
        assert service.read(req_int) == 42

        # 3. Read DINT
        req_dint = PLCReadRequest(
            plc_type="opcua",
            ip="127.0.0.1",
            data_type=DataType.DINT,
            address="ns=2;i=1001"
        )
        assert service.read(req_dint) == 100000

        # 4. Read REAL
        req_real = PLCReadRequest(
            plc_type="opcua",
            ip="127.0.0.1",
            data_type=DataType.REAL,
            address="ns=2;s=Device.Pressure"
        )
        assert service.read(req_real) == 3.14159

        # 5. Read STRING
        req_str = PLCReadRequest(
            plc_type="opcua",
            ip="127.0.0.1",
            data_type=DataType.STRING,
            address="ns=2;s=Device.BatchId"
        )
        assert service.read(req_str) == "Hello OPC-UA"

        # 6. Write INT
        write_int = PLCWriteRequest(
            plc_type="opcua",
            ip="127.0.0.1",
            data_type=DataType.INT,
            address="ns=2;s=Device.RPM",
            value=1200
        )
        assert service.write(write_int) is True
        mock_node.write_value.assert_called()

        # 7. Write BOOL
        write_bool = PLCWriteRequest(
            plc_type="opcua",
            ip="127.0.0.1",
            data_type=DataType.BOOL,
            address="ns=2;s=Device.Start",
            value=True
        )
        assert service.write(write_bool) is True

    finally:
        service.disconnect()


def test_opcua_api_supported_types():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    res = client.get("/api/plc/supported-types")
    assert res.status_code == 200
    types = res.json()
    assert "opcua" in types
