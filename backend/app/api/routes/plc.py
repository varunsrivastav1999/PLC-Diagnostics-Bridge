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
        message="Link active" if connected else "No link",
        connected=connected,
        timestamp=_ts(),
    )


@router.post("/check-port", response_model=PLCResponse)
def check_port_busy(req: PLCConnectRequest):
    """Check detailed port status on the target PLC"""
    
    try:
        port_info = manager.check_port(req)
        # Use PLC-type-aware default ports
        default_ports = {
            'siemens': 102, 'mitsubishi': 5000, 'rockwell': 44818,
            'abb': 502, 'fanuc': 21,
        }
        plc_type_val = req.plc_type.value if hasattr(req.plc_type, 'value') else str(req.plc_type)
        port = req.port if req.port is not None else default_ports.get(plc_type_val, 5000)
        
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


# ──────────── Mitsubishi Port Discovery ────────────

@router.get("/discover-ports")
def discover_ports(ip: str, timeout: float = 1.0):
    """
    Scan Mitsubishi MC Protocol ports on the given IP.
    Returns MC ports, TCP-only ports, reachability, and diagnosis.
    """
    from app.services.plc.mitsubishi import MitsubishiPLCService
    try:
        result = MitsubishiPLCService.discover_ports(ip, timeout=min(timeout, 3.0))
        recommended = result.get('recommended_port')
        mc_ports = result.get('mc_ports', [])
        diagnosis = result.get('diagnosis', '')
        return _ok(
            f"Found {len(mc_ports)} MC Protocol port(s)" if mc_ports else "No MC Protocol ports found",
            connected=False,
            discovery=result,
            recommended_port=recommended,
            diagnosis=diagnosis,
        )
    except Exception as e:
        logger.error(f"Port discovery failed for {ip}: {e}")
        return _fail(f"Port discovery failed: {e}")


@router.get("/discover-subnet")
def discover_subnet(ip: str, timeout: float = 0.5):
    """
    Scan entire /24 subnet to find Mitsubishi PLCs with MC Protocol.
    Checks ports 1025-1040, 5000-5002 and other common MC ports on all 254 IPs.
    Uses 32 concurrent threads for speed (~15-30 seconds).
    """
    from app.services.plc.mitsubishi import MitsubishiPLCService
    try:
        result = MitsubishiPLCService.discover_subnet(ip, timeout=min(timeout, 2.0))
        plcs = result.get('plcs_found', [])
        reachable = result.get('reachable_ips', [])
        subnet = result.get('subnet', '')
        return _ok(
            f"Found {len(plcs)} Mitsubishi PLC(s) on {subnet}" if plcs else f"No Mitsubishi PLCs found on {subnet}",
            connected=False,
            subnet=subnet,
            plcs_found=plcs,
            reachable_ips=reachable,
            total_scanned=result.get('total_scanned', 0),
            scan_time_ms=result.get('scan_time_ms', 0),
        )
    except Exception as e:
        logger.error(f"Subnet discovery failed: {e}")
        return _fail(f"Subnet discovery failed: {e}")

# ──────────── Fanuc Schema ────────────

@router.get("/fanuc/preset-schema")
def get_fanuc_preset_schema():
    """Get dynamic preset schema for Fanuc UI rendering."""
    try:
        from app.services.plc.fxvrlib.library_constants import LibraryConstants
        return _ok("Preset schema retrieved", connected=False, schema=LibraryConstants.PRESET_NAME_TABLES)
    except Exception as e:
        logger.error(f"Failed to get Fanuc preset schema: {e}")
        return _fail(f"Failed to get Fanuc preset schema: {e}")

@router.get("/fanuc/color-schema")
def get_fanuc_color_schema():
    """Get dynamic color schema for Fanuc UI rendering."""
    try:
        from app.services.plc.fxvrlib.library_constants import LibraryConstants
        return _ok("Color schema retrieved", connected=False, 
                   setup_vars=LibraryConstants.COLOR_SETUP_VARS,
                   cycle_vars=LibraryConstants.CYCLE_TIME_VARS,
                   max_colors=LibraryConstants.MAX_COLORS)
    except Exception as e:
        logger.error(f"Failed to get Fanuc color schema: {e}")
        return _fail(f"Failed to get Fanuc color schema: {e}")

@router.post("/fanuc/colors/{color_type}")
def get_fanuc_colors(req: PLCConnectRequest, color_type: str):
    """Fetch color setup or cycle times."""
    try:
        from app.services.plc.fxvrlib.colors import get_color_setup, get_color_cycle_time
        args = {'robot_ip': req.ip}
        if color_type == 'setup':
            data = get_color_setup(args)
        elif color_type == 'cycle':
            data = get_color_cycle_time(args)
        else:
            return _fail(f"Invalid color type: {color_type}")
        return _ok(f"Colors {color_type} fetched", connected=True, value=data)
    except Exception as e:
        logger.error(f"Failed to fetch colors: {e}")
        return _fail(f"Failed to fetch colors: {e}")

@router.put("/fanuc/colors/{color_type}")
def save_fanuc_colors(req: PLCWriteRequest, color_type: str):
    """Write color setup back to the robot controller."""
    try:
        from app.services.plc.fxvrlib.colors import set_color_setup
        if color_type != 'setup':
            return _fail("Only 'setup' type supports write-back. Cycle times are read-only.")
        args = {'robot_ip': req.ip, 'colors': req.value}
        ok = set_color_setup(args)
        if ok:
            return _ok("Color setup saved to robot", connected=True)
        return _fail("set_color_setup returned False")
    except Exception as e:
        logger.error(f"Failed to save colors: {e}")
        return _fail(f"Failed to save colors: {e}")

@router.get("/fanuc/extended-schema")
def get_fanuc_extended_schema():
    """Get dynamic schemas for Manual Settings and GNM/BSC UI rendering."""
    try:
        from app.services.plc.fxvrlib.library_constants import LibraryConstants
        return _ok("Extended schema retrieved", connected=False, 
                   manual_vars=LibraryConstants.MANUAL_SETTINGS_VARS,
                   gnm_bsc_vars=LibraryConstants.GNM_BSC_VARS)
    except Exception as e:
        logger.error(f"Failed to get extended schema: {e}")
        return _fail(f"Failed to get extended schema: {e}")

@router.post("/fanuc/extended/{feature_type}")
def get_fanuc_extended(req: PLCConnectRequest, feature_type: str):
    """Fetch Manual Settings or GNM/BSC."""
    try:
        from app.services.plc.fxvrlib.extended_settings import get_manual_settings, get_gnm_bsc_settings
        args = {'robot_ip': req.ip}
        if req.manual_type:
            args['manual_type'] = req.manual_type
            
        if feature_type == 'manual':
            data = get_manual_settings(args)
        elif feature_type == 'gnmbsc':
            data = get_gnm_bsc_settings(args)
        else:
            return _fail(f"Invalid extended feature type: {feature_type}")
        return _ok(f"Feature {feature_type} fetched", connected=True, value=data)
    except Exception as e:
        logger.error(f"Failed to fetch {feature_type}: {e}")
        return _fail(f"Failed to fetch {feature_type}: {e}")

@router.put("/fanuc/extended/{feature_type}")
def save_fanuc_extended(req: PLCWriteRequest, feature_type: str):
    """Write extended settings back to the robot controller."""
    try:
        from app.services.plc.fxvrlib.extended_settings import set_manual_settings, set_gnm_bsc_settings
        args = {'robot_ip': req.ip, 'data': req.value}
        if feature_type == 'manual':
            ok = set_manual_settings(args)
        elif feature_type == 'gnmbsc':
            ok = set_gnm_bsc_settings(args)
        else:
            return _fail(f"Invalid extended feature type: {feature_type}")
            
        if ok:
            return _ok(f"{feature_type} saved to robot", connected=True)
        return _fail("set returned False")
    except Exception as e:
        logger.error(f"Failed to save {feature_type}: {e}")
        return _fail(f"Failed to save {feature_type}: {e}")

@router.get("/latency")
def get_latency(plc_type: str, ip: str, port: int = None):
    """Get last RPC operation latency for a connection."""
    try:
        service = manager.get_service(
            PLCConnectRequest(plc_type=plc_type, ip=ip, port=port),
            auto_connect=False
        )
        return _ok("Latency retrieved", connected=True, latency_ms=service.get_latency())
    except Exception:
        return _ok("No active connection", connected=False, latency_ms=0)
