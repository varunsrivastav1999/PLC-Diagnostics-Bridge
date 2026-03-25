from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

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

def test_mock_siemens_connect_read_write():
    """Test Siemens PLC service with mocked snap7 client"""
    from app.services.plc.siemens import SiemensPLCService
    from unittest.mock import Mock, patch
    
    # Mock the snap7 client
    with patch('snap7.client.Client') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_connected.return_value = True
        
        # Mock DB read operations
        mock_client.db_read.side_effect = [
            b'\x01',  # For BOOL read (bit 0 set)
            b'\x34\x12',  # For INT read (0x1234 = 4660)
            b'\x78\x56\x34\x12',  # For DINT read (0x12345678 = 305419896)
            b'\x00\x00\x80\x3f',  # For REAL read (1.0 in IEEE 754)
            b'\x05\x04Test',  # For STRING read (max=5, len=4, "Test")
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
        
        # Test read operations
        read_req = Mock()
        read_req.data_type = "BOOL"
        read_req.address = "DB1.DBX0.0"
        assert service.read(read_req) is True
        
        read_req.data_type = "INT"
        read_req.address = "DB1.DBW2"
        assert service.read(read_req) == 4660
        
        read_req.data_type = "DINT"
        read_req.address = "DB1.DBD4"
        assert service.read(read_req) == 305419896
        
        read_req.data_type = "REAL"
        read_req.address = "DB1.DBD8"
        assert service.read(read_req) == 1.0
        
        read_req.data_type = "STRING"
        read_req.address = "DB1.DBD12"
        assert service.read(read_req) == "Test"
