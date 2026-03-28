import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from app.utils.connection_cache import connection_cache, get_plc_id

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_connections():
    connection_cache.clear_all()
    yield
    connection_cache.clear_all()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "2.0.0"}

def test_get_supported_types():
    response = client.get("/api/plc/supported-types")
    assert response.status_code == 200
    types = response.json()
    assert "siemens" in types
    assert "fanuc" in types

def test_mock_fanuc_connect_read_write():
    # Explicit failproof monkeypatching for the isolated Fanuc test
    from app.services.plc.fanuc import FanucPLCService
    FanucPLCService.connect = lambda self, req: True
    FanucPLCService.test_connection = lambda self: True
    FanucPLCService.write = lambda self, req: True
    FanucPLCService.read = lambda self, req: 42
    FanucPLCService.disconnect = lambda self: True
    
    # Fanuc is mocked, so we can test the full flow without real hardware
    conn_payload = {
        "plc_type": "fanuc",
        "ip": "127.0.0.1"
    }
    
    # 1. Connect
    res = client.post("/api/plc/connect", json=conn_payload)
    assert res.status_code == 200
    assert res.json()["success"] is True
    
    # 2. Write
    write_payload = {
        "plc_type": "fanuc",
        "ip": "127.0.0.1",
        "data_type": "INT",
        "address": "SUMMARY.DG",
        "value": 42
    }
    res = client.post("/api/plc/write", json=write_payload)
    assert res.status_code == 200
    assert res.json()["success"] is True

def test_mock_fanuc_write_auto_connects():
    from app.services.plc.fanuc import FanucPLCService
    FanucPLCService.connect = lambda self, req: True
    FanucPLCService.test_connection = lambda self: True
    FanucPLCService.write = lambda self, req: True
    FanucPLCService.disconnect = lambda self: True

    write_payload = {
        "plc_type": "fanuc",
        "ip": "127.0.0.1",
        "data_type": "INT",
        "address": "SUMMARY.DG",
        "value": 42
    }

    res = client.post("/api/plc/write", json=write_payload)
    assert res.status_code == 200
    assert res.json()["success"] is True

def test_connection_cache_distinguishes_plc_type():
    service = object()
    siemens_id = get_plc_id("192.168.0.10", 102, "siemens")
    mitsubishi_id = get_plc_id("192.168.0.10", 102, "mitsubishi")

    assert siemens_id != mitsubishi_id
    connection_cache._connections[siemens_id] = service
    assert connection_cache.get_connection(mitsubishi_id) is None

def test_mock_siemens_address_parsing():
    """Test Siemens address parsing functionality"""
    from app.services.plc.siemens import SiemensPLCService
    
    service = SiemensPLCService()
    
    # Test valid addresses
    assert service._parse_address("DB1.DBX0.0") == (1, "X", 0, 0)
    assert service._parse_address("DB10.DBW2") == (10, "W", 2, 0)
    assert service._parse_address("DB5.DBD4") == (5, "D", 4, 0)
    
    # Test invalid address
    try:
        service._parse_address("INVALID")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

def test_mock_siemens_rejects_word_address_for_bool():
    from app.services.plc.siemens import SiemensPLCService
    from app.schemas.plc import DataType
    from app.core.exceptions import PLCReadError

    service = SiemensPLCService()
    service.client = Mock()

    class MockRequest:
        def __init__(self, data_type, address, bit_offset=0):
            self.data_type = data_type
            self.address = address
            self.bit_offset = bit_offset

    with pytest.raises(PLCReadError):
        service.read(MockRequest(DataType.BOOL, "DB1.DBW0", 0))

def test_mock_siemens_connect_read_write():
    """Test Siemens PLC service with mocked snap7 client"""
    from app.services.plc.siemens import SiemensPLCService
    
    # Mock the snap7 client
    with patch('snap7.client.Client') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_connected.return_value = True
        
        # Mock DB read operations
        mock_client.db_read.side_effect = [
            bytearray(b'\x01'),  # For BOOL read (bit 0 set)
            bytearray(b'\x12\x34'),  # For INT read (0x1234 = 4660)
            bytearray(b'\x12\x34\x56\x78'),  # For DINT read (0x12345678 = 305419896)
            bytearray(b'\x3f\x80\x00\x00'),  # For REAL read (1.0 in IEEE 754)
            bytearray(b'\x05\x04'),  # For STRING header (max=5, len=4)
            bytearray(b'\x05\x04Test'),  # For STRING data (max=5, len=4, "Test")
        ]
        
        service = SiemensPLCService()
        
        # Test connection
        conn_req = Mock()
        conn_req.ip = "192.168.1.100"
        conn_req.rack = 0
        conn_req.slot = 1
        conn_req.port = 102
        
        result = service.connect(conn_req)
        assert result is True
        mock_client.connect.assert_called_once_with("192.168.1.100", 0, 1, tcp_port=102)
        
        # Create a simple request class to avoid Mock issues
        from app.schemas.plc import DataType
        
        class MockRequest:
            def __init__(self, data_type, address, bit_offset=0):
                self.data_type = data_type
                self.address = address
                self.bit_offset = bit_offset
        
        # Test read operations
        read_req = MockRequest(DataType.BOOL, "DB1.DBX0.0", 0)
        assert service.read(read_req) is True
        
        read_req = MockRequest(DataType.INT, "DB1.DBW2", 0)
        assert service.read(read_req) == 4660
        
        read_req = MockRequest(DataType.DINT, "DB1.DBD4", 0)
        assert service.read(read_req) == 305419896
        
        read_req = MockRequest(DataType.REAL, "DB1.DBD8", 0)
        assert service.read(read_req) == 1.0
        
        read_req = MockRequest(DataType.STRING, "DB1.DBD12", 0)
        assert service.read(read_req) == "Test"

def test_mock_mitsubishi_zr_read_write():
    from app.services.plc.mitsubishi import MitsubishiPLCService
    from app.schemas.plc import DataType

    service = MitsubishiPLCService()
    service.client = Mock()
    service.client.batchread_wordunits.return_value = [321]

    class MockReadRequest:
        def __init__(self, data_type, address, register_count=1):
            self.data_type = data_type
            self.address = address
            self.register_count = register_count

    class MockWriteRequest(MockReadRequest):
        def __init__(self, data_type, address, value, register_count=1):
            super().__init__(data_type, address, register_count)
            self.value = value

    assert service.read(MockReadRequest(DataType.INT, "zr100")) == 321
    service.client.batchread_wordunits.assert_called_once_with("ZR100", 1)

    assert service.write(MockWriteRequest(DataType.INT, "zr100", 123)) is True
    service.client.batchwrite_wordunits.assert_called_once_with("ZR100", [123])

def test_mock_fanuc_rejects_unsupported_preset_type():
    from app.services.plc.fanuc import FanucPLCService

    service = FanucPLCService()

    with pytest.raises(ValueError):
        service._parse_address("1,1,ELECTROSTATIC")
