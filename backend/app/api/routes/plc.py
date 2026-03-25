from fastapi import APIRouter
from app.schemas.plc import PLCConnectRequest, PLCReadRequest, PLCWriteRequest, PLCType, DataType
from app.schemas.response import PLCResponse
from app.services.plc.factory import get_plc_service
from app.utils.connection_cache import connection_cache, get_plc_id
import logging
from datetime import datetime, timezone

router = APIRouter()
logger = logging.getLogger(__name__)


def _ts():
    return datetime.now(timezone.utc)


def _ok(msg: str, connected: bool = True, **kwargs) -> PLCResponse:
    return PLCResponse(success=True, message=msg, connected=connected, timestamp=_ts(), **kwargs)


def _fail(msg: str, connected: bool = False, **kwargs) -> PLCResponse:
    return PLCResponse(success=False, message=msg, connected=connected, timestamp=_ts(), **kwargs)


# ──────────── Connection Management ────────────

@router.post("/connect", response_model=PLCResponse)
def connect_plc(req: PLCConnectRequest):
    plc_id = get_plc_id(req.ip, req.port)
    service = connection_cache.get_connection(plc_id)

    if service:
        try:
            if service.test_connection():
                return _ok(f"Already connected to {req.plc_type.value} at {req.ip}", plc_type=req.plc_type.value)
        except Exception:
            connection_cache.remove_connection(plc_id)

    try:
        service = get_plc_service(req.plc_type)
        connected = service.connect(req)
        if connected:
            connection_cache.set_connection(plc_id, service)
            logger.info(f"Connected: {req.plc_type.value} @ {req.ip}:{req.port}")
            return _ok(f"Connected to {req.plc_type.value} at {req.ip}", plc_type=req.plc_type.value)
        return _fail("Connection returned False")
    except Exception as e:
        logger.error(f"Connect failed: {req.plc_type.value} @ {req.ip} — {e}")
        return _fail(str(e))


@router.post("/disconnect", response_model=PLCResponse)
def disconnect_plc(req: PLCConnectRequest):
    plc_id = get_plc_id(req.ip, req.port)
    connection_cache.remove_connection(plc_id)
    logger.info(f"Disconnected: {req.ip}:{req.port}")
    return _ok("Disconnected", connected=False)


@router.post("/test-connection", response_model=PLCResponse)
def test_connection_post(req: PLCConnectRequest):
    plc_id = get_plc_id(req.ip, req.port)
    service = connection_cache.get_connection(plc_id)
    connected = False
    if service:
        try:
            connected = service.test_connection()
        except Exception:
            connected = False
    return PLCResponse(
        success=connected,
        message="Link active" if connected else "No link",
        connected=connected,
        timestamp=_ts(),
    )


# ──────────── Data Operations ────────────

@router.post("/read", response_model=PLCResponse)
def read_value(req: PLCReadRequest):
    plc_id = get_plc_id(req.ip, req.port)
    service = connection_cache.get_connection(plc_id)

    if not service or not service.test_connection():
        try:
            conn_req = PLCConnectRequest(
                plc_type=req.plc_type, ip=req.ip, port=req.port,
                rack=req.rack, slot=req.slot,
            )
            service = get_plc_service(req.plc_type)
            service.connect(conn_req)
            connection_cache.set_connection(plc_id, service)
            logger.info(f"Auto-reconnected: {req.plc_type.value} @ {req.ip}")
        except Exception as e:
            return _fail(f"Not connected, auto-connect failed: {e}")

    try:
        val = service.read(req)
        return _ok("Read OK", value=val, address=req.address, plc_type=req.plc_type.value)
    except Exception as e:
        logger.error(f"Read error [{req.plc_type.value}] {req.address}: {e}")
        return _fail(str(e), connected=True)


@router.post("/write", response_model=PLCResponse)
def write_value(req: PLCWriteRequest):
    plc_id = get_plc_id(req.ip, req.port)
    service = connection_cache.get_connection(plc_id)

    if not service or not service.test_connection():
        return _fail("Not connected to PLC")

    try:
        ok = service.write(req)
        if ok:
            logger.info(f"Write OK [{req.plc_type.value}] {req.address} = {req.value}")
        return _ok("Write OK", address=req.address, plc_type=req.plc_type.value) if ok else _fail("Write returned False", connected=True)
    except Exception as e:
        logger.error(f"Write error [{req.plc_type.value}] {req.address}: {e}")
        return _fail(str(e), connected=True)


# ──────────── Info ────────────

@router.get("/status", response_model=PLCResponse)
def get_status(plc_type: str, ip: str, port: int = None):
    plc_id = get_plc_id(ip, port)
    service = connection_cache.get_connection(plc_id)
    connected = False
    if service:
        try:
            connected = service.test_connection()
        except Exception:
            connected = False
    return PLCResponse(
        success=connected,
        message="Connected" if connected else "Not connected",
        connected=connected,
        timestamp=_ts(),
    )


@router.get("/supported-types", response_model=list[str])
def get_supported_types():
    return [t.value for t in PLCType]
