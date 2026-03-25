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
    
    # 3. Read
    read_payload = {
        "plc_type": "fanuc",
        "ip": "127.0.0.1",
        "data_type": "INT",
        "address": "SUMMARY.DG"
    }
    res = client.post("/api/plc/read", json=read_payload)
    assert res.status_code == 200
    assert res.json()["success"] is True
    assert res.json()["value"] == 42
    
    # 4. Disconnect
    res = client.post("/api/plc/disconnect", json=conn_payload)
    assert res.status_code == 200
    assert res.json()["success"] is True
