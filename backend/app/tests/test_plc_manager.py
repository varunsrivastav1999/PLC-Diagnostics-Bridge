from plcbridge_sdk import ConnectionParams, DataType, PLCManager, ReadParams, WriteParams
from app.services.plc.base import BasePLCService
from app.services.plc.factory import get_plc_service


class DummyPLCService(BasePLCService):
    def __init__(self):
        super().__init__()
        self.last_write = None

    def connect(self, req) -> bool:
        self.is_connected = True
        return True

    def disconnect(self) -> bool:
        self.is_connected = False
        return True

    def test_connection(self) -> bool:
        return self.is_connected

    def read(self, req):
        return {"address": req.address, "data_type": getattr(req.data_type, "value", req.data_type)}

    def write(self, req) -> bool:
        self.last_write = (req.address, req.value)
        return True


def test_custom_driver_can_be_registered_and_resolved():
    PLCManager.register_driver("dummy", DummyPLCService)
    try:
        service = get_plc_service("dummy")
        assert isinstance(service, DummyPLCService)
    finally:
        PLCManager.unregister_driver("dummy")


def test_plc_manager_supports_library_roundtrip():
    manager = PLCManager()
    conn = ConnectionParams(plc_type="dummy", ip="127.0.0.1", port=1234)

    PLCManager.register_driver("dummy", DummyPLCService)
    try:
        assert manager.connect(conn) is True
        assert manager.is_connected(conn) is True
        assert "dummy" in manager.list_supported_types()
        assert manager.active_count == 1

        read_req = ReadParams(
            plc_type="dummy",
            ip="127.0.0.1",
            port=1234,
            data_type=DataType.INT,
            address="R1",
        )
        assert manager.read(read_req) == {"address": "R1", "data_type": "INT"}

        write_req = WriteParams(
            plc_type="dummy",
            ip="127.0.0.1",
            port=1234,
            data_type="INT",
            address="R1",
            value=55,
        )
        assert manager.write(write_req) is True
        assert manager.disconnect(conn) is True
        assert manager.is_connected(conn) is False
    finally:
        manager.clear()
        PLCManager.unregister_driver("dummy")
