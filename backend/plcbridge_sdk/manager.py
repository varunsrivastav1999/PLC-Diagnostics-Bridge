from __future__ import annotations

from typing import Any

from app.core.exceptions import PLCConnectionError
from app.services.plc.base import BasePLCService
from app.services.plc.factory import get_plc_service, get_registered_plc_types, register_plc_service, unregister_plc_service
from app.utils.connection_cache import ConnectionCache, connection_cache, get_plc_id
from app.schemas.plc import PLCConnectRequest, PLCReadRequest, PLCWriteRequest

from .models import ConnectionParams, ReadParams, WriteParams

ConnectRequestLike = PLCConnectRequest | PLCReadRequest | PLCWriteRequest | ConnectionParams | ReadParams | WriteParams
ReadRequestLike = PLCReadRequest | ReadParams
WriteRequestLike = PLCWriteRequest | WriteParams


class PLCManager:
    """Reusable connection manager for SCADA-style apps, scripts, and the FastAPI API layer."""

    def __init__(self, cache: ConnectionCache | None = None):
        self._cache = cache or connection_cache

    def list_supported_types(self) -> list[str]:
        return get_registered_plc_types()

    def connect(self, req: ConnectRequestLike) -> bool:
        plc_id = self._get_cache_key(req)
        cached = self._cache.get_connection(plc_id)

        if cached and self._service_is_alive(cached):
            return True
        if cached:
            self._cache.remove_connection(plc_id)

        connect_req = self._to_connection_params(req)
        service = get_plc_service(connect_req.plc_type)
        if not service.connect(connect_req):
            raise PLCConnectionError(f"Connection returned False for {connect_req.plc_type}")

        self._cache.set_connection(plc_id, service)
        return True

    def disconnect(self, req: ConnectRequestLike) -> bool:
        self._cache.remove_connection(self._get_cache_key(req))
        return True

    def is_connected(self, req: ConnectRequestLike) -> bool:
        service = self._cache.get_connection(self._get_cache_key(req))
        return self._service_is_alive(service) if service else False

    def get_service(self, req: ConnectRequestLike, auto_connect: bool = True) -> BasePLCService:
        plc_id = self._get_cache_key(req)
        service = self._cache.get_connection(plc_id)

        if service and self._service_is_alive(service):
            return service

        if service:
            self._cache.remove_connection(plc_id)

        if not auto_connect:
            raise PLCConnectionError(f"No active connection for {plc_id}")

        self.connect(req)
        service = self._cache.get_connection(plc_id)
        if service is None:
            raise PLCConnectionError(f"Unable to cache connection for {plc_id}")
        return service

    def read(self, req: ReadRequestLike) -> Any:
        plc_id = self._get_cache_key(req)
        service = self.get_service(req, auto_connect=True)
        try:
            return service.read(req)
        except Exception:
            self._cache.remove_connection(plc_id)
            raise

    def write(self, req: WriteRequestLike) -> bool:
        plc_id = self._get_cache_key(req)
        service = self.get_service(req, auto_connect=True)
        try:
            return service.write(req)
        except Exception:
            self._cache.remove_connection(plc_id)
            raise

    def check_port(self, req: ConnectRequestLike) -> dict:
        connect_req = self._to_connection_params(req)
        port = connect_req.port if connect_req.port is not None else 5000
        service = get_plc_service(connect_req.plc_type)
        return service.check_port_busy(connect_req.ip, port)

    def clear(self) -> None:
        self._cache.clear_all()

    @property
    def active_count(self) -> int:
        return self._cache.active_count

    @staticmethod
    def register_driver(plc_type: str, service_cls: type[BasePLCService]) -> None:
        register_plc_service(plc_type, service_cls)

    @staticmethod
    def unregister_driver(plc_type: str) -> None:
        unregister_plc_service(plc_type)

    @staticmethod
    def _get_cache_key(req: ConnectRequestLike) -> str:
        return get_plc_id(req.ip, getattr(req, "port", None), getattr(req, "plc_type", None))

    @staticmethod
    def _service_is_alive(service: BasePLCService) -> bool:
        try:
            return service.test_connection()
        except Exception:
            return False

    @staticmethod
    def _to_connection_params(req: ConnectRequestLike) -> ConnectionParams:
        if isinstance(req, ConnectionParams):
            return req

        return ConnectionParams(
            plc_type=getattr(req, "plc_type"),
            ip=req.ip,
            port=getattr(req, "port", None),
            rack=getattr(req, "rack", 0),
            slot=getattr(req, "slot", 1),
            cpu_type=getattr(req, "cpu_type", None),
        )

