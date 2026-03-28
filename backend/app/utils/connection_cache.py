import threading
import logging
from typing import Dict, Optional
from app.services.plc.base import BasePLCService

logger = logging.getLogger(__name__)


class ConnectionCache:
    """Thread-safe singleton cache for active PLC connections."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._connections: Dict[str, BasePLCService] = {}
                cls._instance._conn_lock = threading.Lock()
        return cls._instance

    def get_connection(self, plc_id: str) -> Optional[BasePLCService]:
        with self._conn_lock:
            return self._connections.get(plc_id)

    def set_connection(self, plc_id: str, service: BasePLCService):
        with self._conn_lock:
            # Disconnect existing if replacing
            existing = self._connections.get(plc_id)
            if existing:
                try:
                    existing.disconnect()
                except Exception:
                    pass
            self._connections[plc_id] = service
            logger.info(f"Connection cached: {plc_id}")

    def remove_connection(self, plc_id: str):
        with self._conn_lock:
            service = self._connections.pop(plc_id, None)
            if service:
                try:
                    service.disconnect()
                except Exception:
                    pass
                logger.info(f"Connection removed: {plc_id}")

    def clear_all(self):
        with self._conn_lock:
            for plc_id, service in list(self._connections.items()):
                try:
                    service.disconnect()
                except Exception:
                    pass
            self._connections.clear()
            logger.info("All connections cleared")

    @property
    def active_count(self) -> int:
        with self._conn_lock:
            return len(self._connections)


connection_cache = ConnectionCache()


def get_plc_id(ip: str, port: Optional[int] = None, plc_type: Optional[object] = None) -> str:
    plc_type_value = getattr(plc_type, "value", plc_type)
    base_id = f"{ip}:{port}" if port is not None else ip
    return f"{plc_type_value}@{base_id}" if plc_type_value else base_id
