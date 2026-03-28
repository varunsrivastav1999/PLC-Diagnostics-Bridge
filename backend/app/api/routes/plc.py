from fastapi import APIRouter
from app.schemas.plc import PLCConnectRequest, PLCReadRequest, PLCWriteRequest
from app.schemas.response import PLCResponse
import logging
from datetime import datetime, timezone
from plcbridge_sdk.manager import PLCManager

router = APIRouter()
logger = logging.getLogger(__name__)
manager = PLCManager()


def _ts():
    return datetime.now(timezone.utc)


def _ok(msg: str, connected: bool = True, **kwargs) -> PLCResponse:
    return PLCResponse(success=True, message=msg, connected=connected, timestamp=_ts(), **kwargs)


def _fail(msg: str, connected: bool = False, **kwargs) -> PLCResponse:
    return PLCResponse(success=False, message=msg, connected=connected, timestamp=_ts(), **kwargs)


# ──────────── Connection Management ────────────

@router.post("/connect", response_model=PLCResponse)
def connect_plc(req: PLCConnectRequest):
    try:
        already_connected = manager.is_connected(req)
        manager.connect(req)
        message = f"Already connected to {req.plc_type.value} at {req.ip}" if already_connected else f"Connected to {req.plc_type.value} at {req.ip}"
        logger.info(f"Connected: {req.plc_type.value} @ {req.ip}:{req.port}")
        return _ok(message, plc_type=req.plc_type.value)
    except Exception as e:
        logger.error(f"Connect failed: {req.plc_type.value} @ {req.ip} — {e}")
        return _fail(str(e))


@router.post("/disconnect", response_model=PLCResponse)
def disconnect_plc(req: PLCConnectRequest):
    manager.disconnect(req)
    logger.info(f"Disconnected: {req.ip}:{req.port}")
    return _ok("Disconnected", connected=False)


@router.post("/test-connection", response_model=PLCResponse)
def test_connection_post(req: PLCConnectRequest):
    try:
        connected = manager.is_connected(req)
    except Exception:
        connected = False
    return PLCResponse(
        success=connected,
        message="Link active (closed)" if connected else "No link",
        connected=connected,
        timestamp=_ts(),
    )


@router.post("/check-port", response_model=PLCResponse)
def check_port_busy(req: PLCConnectRequest):
    """Check detailed port status on the target PLC"""
    
    try:
        port_info = manager.check_port(req)
        port = req.port if req.port is not None else 5000
        
        # For backward compatibility, keep port_busy field
        is_busy = port_info.get('busy', False)
        
        return _ok(
            port_info.get('message', f"Port {port} status checked"),
            connected=is_busy,
            port_busy=is_busy,
            port_status=port_info.get('status', 'unknown'),
            response_time=port_info.get('response_time')
        )
    except Exception as e:
        logger.error(f"Port check failed: {e}")
        return _fail(f"Port check failed: {e}", port_busy=False, port_status='error')


# ──────────── Data Operations ────────────

@router.post("/read", response_model=PLCResponse)
def read_value(req: PLCReadRequest):
    try:
        val = manager.read(req)
    except Exception as e:
        logger.error(f"Read error [{req.plc_type.value}] {req.address}: {e}")
        return _fail(str(e), connected=False)

    return _ok("Read OK", value=val, address=req.address, plc_type=req.plc_type.value, connected=True)


@router.post("/write", response_model=PLCResponse)
def write_value(req: PLCWriteRequest):
    try:
        ok = manager.write(req)
        if ok:
            logger.info(f"Write OK [{req.plc_type.value}] {req.address} = {req.value}")
    except Exception as e:
        logger.error(f"Write error [{req.plc_type.value}] {req.address}: {e}")
        return _fail(str(e), connected=False)

    return _ok("Write OK", address=req.address, plc_type=req.plc_type.value, connected=True) if ok else _fail("Write returned False", connected=False)


# ──────────── Info ────────────

@router.get("/status", response_model=PLCResponse)
def get_status(plc_type: str, ip: str, port: int = None):
    connected = manager.is_connected(PLCConnectRequest(plc_type=plc_type, ip=ip, port=port))
    return PLCResponse(
        success=connected,
        message="Connected" if connected else "Not connected",
        connected=connected,
        timestamp=_ts(),
    )


@router.get("/supported-types", response_model=list[str])
def get_supported_types():
    return manager.list_supported_types()
