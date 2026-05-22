import struct
import re
import threading
import queue
import logging
from typing import Any
from enum import Enum

import pymcprotocol
from app.services.plc.base import BasePLCService
from app.schemas.plc import PLCConnectRequest, PLCReadRequest, PLCWriteRequest, DataType
from app.core.exceptions import PLCConnectionError, PLCReadError, PLCWriteError

logger = logging.getLogger(__name__)


class _OpType(Enum):
    READ = "read"
    WRITE = "write"


class _RPCRequest:
    """A single queued RPC operation with its result future."""
    __slots__ = ('op', 'req', 'result', 'error', 'done')

    def __init__(self, op: _OpType, req: Any):
        self.op = op
        self.req = req
        self.result: Any = None
        self.error: Exception | None = None
        self.done = threading.Event()


class MitsubishiPLCService(BasePLCService):
    """
    Mitsubishi PLC Service using MC Protocol (MELSEC Communication Protocol).
    Compatible with Q Series, L Series, and FX Series (including FX5U-500B).
    Uses Type3E Ethernet protocol for reliable industrial communication.

    All read/write operations are serialized through an internal RPC queue
    to prevent concurrent access to the single TCP socket used by pymcprotocol.
    This eliminates BrokenPipe, connection-reset, and garbled-data errors
    when the frontend polls while a write is in progress.
    """
    def __init__(self):
        super().__init__()
        self.client: pymcprotocol.Type3E | None = None
        # RPC queue for serializing all PLC I/O through one socket
        self._op_queue: queue.Queue[_RPCRequest | None] = queue.Queue(maxsize=256)
        self._worker: threading.Thread | None = None
        self._lock = threading.Lock()  # protects connect/disconnect vs. worker lifecycle
        self._ip: str = ""
        self._port: int = 5000

    # ───────────────────── Worker Thread ─────────────────────

    def _start_worker(self):
        """Start the background worker that drains the operation queue."""
        if self._worker is not None and self._worker.is_alive():
            return
        self._worker = threading.Thread(
            target=self._worker_loop,
            name=f"mitsubishi-rpc-{self._ip}:{self._port}",
            daemon=True,
        )
        self._worker.start()
        logger.info(f"Mitsubishi RPC worker started for {self._ip}:{self._port}")

    def _stop_worker(self):
        """Send a poison pill to gracefully stop the worker."""
        if self._worker is None or not self._worker.is_alive():
            return
        self._op_queue.put(None)  # poison pill
        self._worker.join(timeout=3.0)
        self._worker = None
        # Drain any pending requests so callers don't hang
        while not self._op_queue.empty():
            try:
                rpc = self._op_queue.get_nowait()
                if rpc is not None:
                    rpc.error = PLCConnectionError("Mitsubishi connection closed while request was pending")
                    rpc.done.set()
            except queue.Empty:
                break

    def _worker_loop(self):
        """Continuously dequeue and execute PLC operations one at a time."""
        while True:
            rpc = self._op_queue.get()
            if rpc is None:
                # Poison pill → exit
                logger.debug("Mitsubishi RPC worker received stop signal")
                break
            try:
                if rpc.op == _OpType.READ:
                    rpc.result = self._do_read(rpc.req)
                elif rpc.op == _OpType.WRITE:
                    rpc.result = self._do_write(rpc.req)
            except Exception as e:
                rpc.error = e
            finally:
                rpc.done.set()

    def _enqueue(self, op: _OpType, req: Any, timeout: float = 10.0) -> Any:
        """
        Submit an operation to the RPC queue and block until it completes.
        This is the ONLY path through which read/write hits the socket.
        """
        if not self.is_connected:
            raise PLCConnectionError("Mitsubishi PLC not connected")
        if self._worker is None or not self._worker.is_alive():
            self.is_connected = False
            raise PLCConnectionError("Mitsubishi RPC worker is not running — reconnect required")

        rpc = _RPCRequest(op, req)
        try:
            self._op_queue.put(rpc, timeout=2.0)
        except queue.Full:
            raise PLCReadError("Mitsubishi operation queue full — PLC may be unresponsive") if op == _OpType.READ else PLCWriteError("Mitsubishi operation queue full — PLC may be unresponsive")

        # Wait for the worker to execute our request
        if not rpc.done.wait(timeout=timeout):
            raise PLCReadError("Mitsubishi operation timed out") if op == _OpType.READ else PLCWriteError("Mitsubishi operation timed out")

        if rpc.error is not None:
            raise rpc.error
        return rpc.result

    # ───────────────────── Port Discovery ─────────────────────

    @classmethod
    def discover_ports(cls, ip: str, timeout: float = 1.0) -> dict:
        """
        Scan Mitsubishi MC Protocol ports and return discovery results.
        Includes network reachability check and wide port scan.
        """
        import socket
        import subprocess
        import time

        start = time.monotonic()

        # ── Phase 0: Check if IP is reachable via ping ──
        reachable = False
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '1', ip],
                capture_output=True, timeout=3
            )
            reachable = result.returncode == 0
        except Exception:
            # ping may not be available on all systems; treat as unknown
            pass

        mc_ports = []
        tcp_ports = []
        closed_count = 0

        # Wide scan: common Mitsubishi / industrial Ethernet ports
        scan_ports = cls.COMMON_MC_PORTS

        for port in scan_ports:
            # Phase 1: Fast TCP probe
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                sock.close()
            except Exception:
                closed_count += 1
                continue

            if result != 0:
                closed_count += 1
                continue

            # Phase 2: MC Protocol handshake on open ports
            client = pymcprotocol.Type3E()
            mc_ok = False
            try:
                client.connect(ip, port)
                try:
                    client.batchread_bitunits(headdevice="M0", readsize=1)
                    mc_ok = True
                except Exception:
                    try:
                        client.batchread_wordunits(headdevice="D0", readsize=1)
                        mc_ok = True
                    except Exception:
                        pass
            except Exception:
                pass
            finally:
                try:
                    client.close()
                except Exception:
                    pass

            if mc_ok:
                mc_ports.append(port)
            else:
                tcp_ports.append(port)

        scan_time = round((time.monotonic() - start) * 1000, 1)

        # ── Build diagnosis ──
        if mc_ports:
            diagnosis = f"MC Protocol found on port(s): {mc_ports}. Ready to connect."
        elif tcp_ports:
            diagnosis = (
                f"IP {ip} is reachable and has TCP port(s) open: {tcp_ports}, "
                f"but none responded to MC Protocol. "
                f"Possible causes: (1) MC Protocol not enabled in GX Works PLC parameters, "
                f"(2) PLC is in STOP mode, (3) Open port belongs to another service (HTTP, FTP, etc)."
            )
        elif reachable:
            diagnosis = (
                f"IP {ip} is reachable (ping OK) but all {len(scan_ports)} scanned ports are closed. "
                f"MC Protocol TCP listener is not configured. "
                f"Fix: Open GX Works → PLC Parameters → Built-in Ethernet / Ethernet Module → "
                f"Open Settings → Enable MC Protocol on a TCP port (e.g. 5000)."
            )
        else:
            diagnosis = (
                f"IP {ip} is NOT reachable (ping failed). "
                f"Check: (1) PLC is powered on, (2) Ethernet cable connected, "
                f"(3) IP address is correct, (4) PC and PLC are on the same subnet."
            )

        return {
            'ip': ip,
            'reachable': reachable,
            'mc_ports': mc_ports,
            'tcp_ports': tcp_ports,
            'closed_count': closed_count,
            'ports_scanned': len(scan_ports),
            'recommended_port': mc_ports[0] if mc_ports else None,
            'scan_time_ms': scan_time,
            'diagnosis': diagnosis,
        }

    # Common Mitsubishi MC Protocol port range used by Q/L/FX/iQ series
    COMMON_MC_PORTS = [5000, 5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009, 5010,
                       5011, 5012, 5013, 5014, 5015, 5016, 5017, 5018, 5019, 5020,
                       5100, 5101, 5102, 5103, 5104, 5105,
                       4999, 4998, 4997,
                       2000, 2001, 2002, 2003, 2004, 2005,
                       3000, 3001, 3002, 3003, 3004, 3005,
                       4000, 4001, 4002,
                       1000, 1025, 1026, 1027, 1028,
                       6000, 6001, 6002,
                       8000, 8001]

    def _try_tcp_connect(self, ip: str, port: int, timeout: float = 1.0) -> bool:
        """Fast TCP handshake probe — checks if anything is listening on ip:port."""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def _try_mc_connect(self, ip: str, port: int) -> bool:
        """Attempt a full MC Protocol handshake: TCP + test read."""
        self.client = pymcprotocol.Type3E()
        try:
            self.client.connect(ip, port)
        except Exception:
            self.client = None
            return False

        # Verify MC Protocol communication with test reads
        try:
            self.client.batchread_bitunits(headdevice="M0", readsize=1)
            return True
        except Exception:
            pass
        try:
            self.client.batchread_wordunits(headdevice="D0", readsize=1)
            return True
        except Exception:
            pass

        # TCP connected but MC Protocol not responding
        try:
            self.client.close()
        except Exception:
            pass
        self.client = None
        return False

    def connect(self, req: PLCConnectRequest) -> bool:
        with self._lock:
            # Clean up any existing connection first
            if self.is_connected or self._worker is not None:
                self._stop_worker()
                if self.client is not None:
                    try:
                        self.client.close()
                    except Exception:
                        pass
                self.is_connected = False
                self.client = None

            user_port = req.port if req.port is not None else 5000
            self._ip = req.ip

            # ── Phase 1: Try the user-specified port directly ──
            if self._try_mc_connect(req.ip, user_port):
                self._port = user_port
                self.is_connected = True
                self._op_queue = queue.Queue(maxsize=256)
                self._start_worker()
                logger.info(f"Mitsubishi connected: {req.ip}:{user_port} (RPC queue active)")
                return True

            # ── Phase 2: Auto-discover — scan common MC Protocol ports ──
            scanned_ports = [p for p in self.COMMON_MC_PORTS if p != user_port]

            logger.info(f"Mitsubishi port {user_port} refused on {req.ip}, scanning common MC Protocol ports...")

            for port in scanned_ports:
                if self._try_tcp_connect(req.ip, port):
                    logger.debug(f"  TCP open on {req.ip}:{port}, trying MC Protocol...")
                    if self._try_mc_connect(req.ip, port):
                        self._port = port
                        self.is_connected = True
                        self._op_queue = queue.Queue(maxsize=256)
                        self._start_worker()
                        logger.info(
                            f"Mitsubishi auto-discovered on port {port} "
                            f"(user specified {user_port}). Connected: {req.ip}:{port}"
                        )
                        return True

            # ── Phase 3: All ports failed — give clear diagnostics ──
            self.is_connected = False
            self.client = None
            raise PLCConnectionError(
                f"Mitsubishi connection refused at {req.ip}:{user_port}. "
                f"Auto-scan of ports {scanned_ports[:6]}... also failed. "
                f"Check: (1) PLC Ethernet module has MC Protocol (TCP) enabled in GX Works, "
                f"(2) the configured port number matches, "
                f"(3) PLC is in RUN mode, "
                f"(4) firewall allows TCP to PLC IP."
            )

    def disconnect(self) -> bool:
        with self._lock:
            self._stop_worker()
            if self.client is not None:
                try:
                    self.client.close()
                except Exception:
                    pass
                self.client = None
            self.is_connected = False
            return True

    def test_connection(self) -> bool:
        if not self.is_connected:
            return False
        try:
            # Use the RPC queue so this doesn't race with ongoing I/O
            self._enqueue(_OpType.READ, _TestReq(), timeout=3.0)
            return True
        except Exception:
            self.is_connected = False
            return False

    # ───────────────────── Public Read / Write ─────────────────────

    def read(self, req: PLCReadRequest) -> Any:
        return self._enqueue(_OpType.READ, req)

    def write(self, req: PLCWriteRequest) -> bool:
        return self._enqueue(_OpType.WRITE, req)

    # ───────────────────── Internal I/O (worker thread only) ─────────────────────

    def _words_to_bytes(self, words: list[int]) -> bytes:
        """Convert list of 16-bit word values to bytes (little-endian per word)."""
        result = bytearray()
        for w in words:
            result.extend(struct.pack('<H', w & 0xFFFF))
        return bytes(result)

    def _bytes_to_words(self, data: bytes) -> list[int]:
        """Convert bytes to list of 16-bit word values."""
        # Pad to even length
        if len(data) % 2 != 0:
            data = data + b'\x00'
        words = []
        for i in range(0, len(data), 2):
            words.append(struct.unpack('<H', data[i:i+2])[0])
        return words

    def _normalize_headdevice(self, address: str) -> str:
        """Normalize Mitsubishi device names so tags like `zr100` work reliably."""
        headdevice = re.sub(r"\s+", "", address or "").upper()
        if not re.fullmatch(r"[A-Z]+[0-9A-F]+", headdevice):
            raise ValueError(f"Invalid Mitsubishi address: {address}")
        return headdevice

    def _do_read(self, req) -> Any:
        """Execute a read on the worker thread. Never call from outside the worker."""
        if self.client is None:
            raise PLCConnectionError("Mitsubishi client not initialized")

        # Handle internal test_connection probe
        if isinstance(req, _TestReq):
            try:
                self.client.batchread_bitunits(headdevice="M0", readsize=1)
            except Exception:
                self.client.batchread_wordunits(headdevice="D0", readsize=1)
            return True

        try:
            headdevice = self._normalize_headdevice(req.address)

            if req.data_type == DataType.BOOL:
                bit_data = self.client.batchread_bitunits(headdevice, 1)
                return bool(bit_data[0]) if bit_data else False

            elif req.data_type == DataType.INT:
                word_data = self.client.batchread_wordunits(headdevice, 1)
                val = word_data[0] if word_data else 0
                # Sign-extend 16-bit to signed int
                if val > 32767:
                    val -= 65536
                return val

            elif req.data_type == DataType.DINT:
                # 32-bit integer = 2 consecutive D registers
                word_data = self.client.batchread_wordunits(headdevice, 2)
                if len(word_data) >= 2:
                    raw = self._words_to_bytes(word_data[:2])
                    return struct.unpack('<i', raw)[0]
                return 0

            elif req.data_type in (DataType.REAL, DataType.FLOAT):
                # 32-bit float = 2 consecutive D registers
                word_data = self.client.batchread_wordunits(headdevice, 2)
                if len(word_data) >= 2:
                    raw = self._words_to_bytes(word_data[:2])
                    return round(struct.unpack('<f', raw)[0], 6)
                return 0.0

            elif req.data_type == DataType.STRING:
                # STRING: each D register holds 2 ASCII characters
                reg_count = getattr(req, 'register_count', 10) or 10
                word_data = self.client.batchread_wordunits(headdevice, reg_count)
                raw = self._words_to_bytes(word_data)
                text = raw.decode('ascii', errors='replace').rstrip('\x00').rstrip()
                return text

            else:
                word_data = self.client.batchread_wordunits(headdevice, 1)
                return word_data[0] if word_data else 0

        except Exception as e:
            raise PLCReadError(f"Mitsubishi read failed: {e}")

    def _do_write(self, req: PLCWriteRequest) -> bool:
        """Execute a write on the worker thread. Never call from outside the worker."""
        if self.client is None:
            raise PLCConnectionError("Mitsubishi client not initialized")
        try:
            headdevice = self._normalize_headdevice(req.address)

            if req.data_type == DataType.BOOL:
                self.client.batchwrite_bitunits(headdevice, [int(bool(req.value))])

            elif req.data_type == DataType.INT:
                val = int(req.value) & 0xFFFF
                self.client.batchwrite_wordunits(headdevice, [val])

            elif req.data_type == DataType.DINT:
                raw = struct.pack('<i', int(req.value))
                words = self._bytes_to_words(raw)
                self.client.batchwrite_wordunits(headdevice, words)

            elif req.data_type in (DataType.REAL, DataType.FLOAT):
                raw = struct.pack('<f', float(req.value))
                words = self._bytes_to_words(raw)
                self.client.batchwrite_wordunits(headdevice, words)

            elif req.data_type == DataType.STRING:
                reg_count = getattr(req, 'register_count', 10) or 10
                text = str(req.value)
                byte_len = reg_count * 2
                encoded = text.encode('ascii', errors='replace')[:byte_len]
                encoded = encoded.ljust(byte_len, b'\x00')
                words = self._bytes_to_words(encoded)
                self.client.batchwrite_wordunits(headdevice, words)

            else:
                self.client.batchwrite_wordunits(headdevice, [int(req.value)])

            return True
        except Exception as e:
            raise PLCWriteError(f"Mitsubishi write failed: {e}")


class _TestReq:
    """Lightweight sentinel for internal test_connection probes via the RPC queue."""
    pass
