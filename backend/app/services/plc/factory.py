from __future__ import annotations

from collections.abc import Callable

from app.schemas.plc import PLCType
from app.services.plc.base import BasePLCService


def _normalize_plc_type(plc_type: PLCType | str) -> str:
    return getattr(plc_type, "value", str(plc_type))


_BUILTIN_SERVICE_LOADERS: dict[str, Callable[[], type[BasePLCService]]] = {
    PLCType.siemens.value: lambda: __import__("app.services.plc.siemens", fromlist=["SiemensPLCService"]).SiemensPLCService,
    PLCType.mitsubishi.value: lambda: __import__("app.services.plc.mitsubishi", fromlist=["MitsubishiPLCService"]).MitsubishiPLCService,
    PLCType.rockwell.value: lambda: __import__("app.services.plc.rockwell", fromlist=["RockwellPLCService"]).RockwellPLCService,
    PLCType.abb.value: lambda: __import__("app.services.plc.abb", fromlist=["ABBPLCService"]).ABBPLCService,
    PLCType.fanuc.value: lambda: __import__("app.services.plc.fanuc", fromlist=["FanucPLCService"]).FanucPLCService,
}

_CUSTOM_SERVICE_REGISTRY: dict[str, type[BasePLCService]] = {}


def register_plc_service(plc_type: PLCType | str, service_cls: type[BasePLCService]) -> None:
    if not issubclass(service_cls, BasePLCService):
        raise TypeError("service_cls must inherit from BasePLCService")
    _CUSTOM_SERVICE_REGISTRY[_normalize_plc_type(plc_type)] = service_cls


def unregister_plc_service(plc_type: PLCType | str) -> None:
    _CUSTOM_SERVICE_REGISTRY.pop(_normalize_plc_type(plc_type), None)


def get_registered_plc_types() -> list[str]:
    return sorted(set(_BUILTIN_SERVICE_LOADERS.keys()) | set(_CUSTOM_SERVICE_REGISTRY.keys()))


def get_plc_service(plc_type: PLCType | str) -> BasePLCService:
    plc_key = _normalize_plc_type(plc_type)

    service_cls = _CUSTOM_SERVICE_REGISTRY.get(plc_key)
    if service_cls is not None:
        return service_cls()

    loader = _BUILTIN_SERVICE_LOADERS.get(plc_key)
    if loader is None:
        raise ValueError(f"Unsupported PLC type: {plc_key}")

    return loader()()
