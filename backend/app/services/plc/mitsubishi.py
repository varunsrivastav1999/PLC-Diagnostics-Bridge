import struct
import re
import threading
import queue
import logging
from typing import Any
from enum import Enum

import pymcprotocol
from app.services.plc.base import BasePLCService
import app.services.plc.base as base
from app.schemas.plc import PLCConnectRequest, PLCReadRequest, PLCWriteRequest, DataType
from app.core.exceptions import PLCConnectionError, PLCReadError, PLCWriteError

logger = logging.getLogger(__name__)




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
            # Note: We append ALL open ports to mc_ports because the strict Type3E binary handshake
            # might fail (Connection Reset) if the port is configured for Type4E or ASCII,
            # yet it is still the correct MC Protocol port.
            mc_ports.append(port)
            
            client = pymcprotocol.Type3E()
            try:
                client.connect(ip, port)
                try:
                    client.batchread_bitunits(headdevice="M0", readsize=1)
                except Exception as e:
                    err_str = str(e).lower()
                    if "timeout" not in err_str and "timed out" not in err_str and "connection" not in err_str:
                        pass
                    else:
                        try:
                            client.batchread_wordunits(headdevice="D0", readsize=1)
                        except Exception:
                            pass
            except Exception:
                pass
            finally:
                try:
                    client.close()
                except Exception:
                    pass

        scan_time = round((time.monotonic() - start) * 1000, 1)

        # ── Build diagnosis ──
        if mc_ports:
            diagnosis = f"Found open PLC port(s): {mc_ports}. Ready to connect."
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
                       1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032,
                       1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040,
                       1000, 1001, 1002,
                       2000, 2001, 2002, 2003, 2004, 2005,
                       3000, 3001, 3002, 3003, 3004, 3005,
                       4000, 4001, 4002,
                       6000, 6001, 6002,
                       8000, 8001]

    # Quick ports for subnet scan (fast check per IP)
    QUICK_MC_PORTS = [5000, 5001, 5002, 1025, 1026, 1027, 1028, 1029, 1030,
                      1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040,
                      2000, 3000, 4999, 5100]

    @classmethod
    def discover_subnet(cls, base_ip: str, timeout: float = 0.5) -> dict:
        """
        Scan an entire /24 subnet to find Mitsubishi PLCs with MC Protocol.
        Uses concurrent threads for speed (scans 254 IPs in ~15-30 seconds).

        Args:
            base_ip: Any IP in the subnet (e.g. "192.169.4.152")
            timeout: TCP timeout per port probe

        Returns:
            {
                'subnet': '192.169.4.0/24',
                'plcs_found': [
                    {'ip': '192.169.4.10', 'mc_ports': [5000], 'tcp_ports': [80]},
                    ...
                ],
                'reachable_ips': ['192.169.4.1', '192.169.4.10', ...],
                'scan_time_ms': 12400.5,
            }
        """
        import socket
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed

        # Extract subnet base
        parts = base_ip.strip().split('.')
        if len(parts) != 4:
            return {'error': f'Invalid IP: {base_ip}', 'plcs_found': [], 'reachable_ips': []}
        subnet_base = '.'.join(parts[:3])

        start = time.monotonic()
        plcs_found = []
        reachable_ips = []
        lock = threading.Lock()

        def probe_ip(ip: str):
            """Probe a single IP for MC Protocol ports."""
            mc_ports_found = []
            tcp_ports_found = []

            for port in cls.QUICK_MC_PORTS:
                # Fast TCP probe
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(timeout)
                    result = sock.connect_ex((ip, port))
                    sock.close()
                except Exception:
                    continue

                if result != 0:
                    continue

                # Port is open. Add as a candidate PLC port immediately,
                # since strict MC Protocol handshakes often fail on non-binary ports.
                mc_ports_found.append(port)

                # Optional: still test handshake but don't strictly require success
                client = pymcprotocol.Type3E()
                try:
                    client.connect(ip, port)
                    try:
                        client.batchread_bitunits(headdevice="M0", readsize=1)
                    except Exception as e:
                        err_str = str(e).lower()
                        if "timeout" not in err_str and "timed out" not in err_str and "connection" not in err_str:
                            pass
                        else:
                            try:
                                client.batchread_wordunits(headdevice="D0", readsize=1)
                            except Exception:
                                pass
                except Exception:
                    pass
                finally:
                    try:
                        client.close()
                    except Exception:
                        pass

            with lock:
                if mc_ports_found or tcp_ports_found:
                    reachable_ips.append(ip)
                if mc_ports_found:
                    plcs_found.append({
                        'ip': ip,
                        'mc_ports': mc_ports_found,
                        'tcp_ports': tcp_ports_found,
                    })

        # Scan all 254 IPs concurrently (skip .0 and .255)
        ips_to_scan = [f"{subnet_base}.{i}" for i in range(1, 255)]

        with ThreadPoolExecutor(max_workers=32) as executor:
            futures = {executor.submit(probe_ip, ip): ip for ip in ips_to_scan}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception:
                    pass

        scan_time = round((time.monotonic() - start) * 1000, 1)

        # Sort by IP
        plcs_found.sort(key=lambda x: [int(p) for p in x['ip'].split('.')])
        reachable_ips.sort(key=lambda x: [int(p) for p in x.split('.')])

        return {
            'subnet': f'{subnet_base}.0/24',
            'plcs_found': plcs_found,
            'reachable_ips': reachable_ips,
            'total_scanned': len(ips_to_scan),
            'scan_time_ms': scan_time,
        }

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
                self._start_worker(f"mitsubishi-{self._ip}:{self._port}")
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
                        self._start_worker(f"mitsubishi-{self._ip}:{self._port}")
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
            self._enqueue(_OpType.READ, base._TestReq(), timeout=3.0)
            return True
        except Exception:
            self.is_connected = False
            return False

    # ───────────────────── Internal I/O (worker thread only) ─────────────────────

    # Valid Mitsubishi device prefixes (word + bit)
    VALID_DEVICES_WORD = {'D', 'W', 'R', 'ZR', 'TN', 'CN', 'SD'}
    VALID_DEVICES_BIT = {'M', 'X', 'Y', 'B', 'L', 'SM', 'TS', 'CS', 'F'}
    VALID_DEVICES = VALID_DEVICES_WORD | VALID_DEVICES_BIT

    def _words_to_bytes(self, words: list[int]) -> bytes:
        """
        Convert list of 16-bit word values to bytes for STRING decoding.

        Mitsubishi MC Protocol stores ASCII strings in each 16-bit register as:
          Low  byte (bits 0-7)  → 1st character (even position)
          High byte (bits 8-15) → 2nd character (odd position)

        pymcprotocol returns words in native format, so we use little-endian
        unpacking: struct.pack('<H', word) → [low_byte, high_byte]
        which gives the correct character order.
        """
        result = bytearray()
        for w in words:
            result.extend(struct.pack('<H', w & 0xFFFF))
        return bytes(result)

    def _words_to_bytes_swapped(self, words: list[int]) -> bytes:
        """
        Alternate byte order: high byte first, then low byte.
        Used as fallback if the standard order produces non-printable output.
        """
        result = bytearray()
        for w in words:
            result.extend(struct.pack('>H', w & 0xFFFF))
        return bytes(result)

    def _bytes_to_words(self, data: bytes) -> list[int]:
        """Convert bytes to list of 16-bit word values (little-endian)."""
        # Pad to even length
        if len(data) % 2 != 0:
            data = data + b'\x00'
        words = []
        for i in range(0, len(data), 2):
            words.append(struct.unpack('<H', data[i:i+2])[0])
        return words

    def _normalize_headdevice(self, address: str) -> str:
        address = address.strip().upper()
        if not address:
            raise ValueError("Address cannot be empty")
        return address

    def _advance_headdevice(self, headdevice: str, offset: int) -> str:
        import re
        match = re.match(r"^([a-zA-Z\*]+)([a-fA-F0-9]+)$", headdevice)
        if not match:
            return headdevice # fallback
        
        prefix = match.group(1).upper()
        num_str = match.group(2)
        
        # Hex based devices in Mitsubishi
        is_hex = prefix in ("X", "Y", "B", "W", "SW", "DX", "DY")
        base = 16 if is_hex else 10
        
        num = int(num_str, base)
        new_num = num + offset
        
        if is_hex:
            return f"{prefix}{new_num:X}"
        else:
            return f"{prefix}{new_num}"
        """
        Normalize Mitsubishi device names with proper device prefix validation.
        Supports: D, W, R, ZR, M, X, Y, B, L, SM, TN, CN, TS, CS, SD
        Examples: 'D100', 'ZR0', 'ZR10', 'M10', 'W1F' (hex for bit/link devices)
        """
        headdevice = re.sub(r"\s+", "", address or "").upper()

        # Extract device prefix and numeric part
        match = re.fullmatch(r'([A-Z]{1,2})(\d+)', headdevice)
        is_decimal_match = bool(match)
        if not match:
            # Also allow hex addresses for link/bit devices (W, B, X, Y)
            match = re.fullmatch(r'([A-Z]{1,2})([0-9A-F]+)', headdevice)
            if not match:
                raise ValueError(
                    f"Invalid Mitsubishi address format: '{address}'. "
                    f"Expected format: DEVICE + NUMBER (e.g. D100, ZR0, M10)"
                )

        prefix = match.group(1)
        num_str = match.group(2)

        if prefix not in self.VALID_DEVICES:
            raise ValueError(
                f"Unknown Mitsubishi device prefix: '{prefix}' in address '{address}'. "
                f"Valid devices: {', '.join(sorted(self.VALID_DEVICES))}"
            )

        # BUGFIX: pymcprotocol treats ZR registers as hexadecimal (base 16).
        # However, users and GX Works always address ZR registers in decimal.
        # E.g., if a user asks for ZR10 (offset 10 decimal), pymcprotocol 
        # reads it as int("10", 16) = offset 16.
        # We intercept decimal ZR requests and convert them to a hex string.
        # NOTE: We MUST zero-pad the hex string (e.g. 10 -> 00000A) because if 
        # the hex string consists entirely of letters (e.g. 'A'), pymcprotocol's
        # regex will misinterpret 'ZRA' as a device prefix and crash.
        if prefix == 'ZR' and is_decimal_match:
            decimal_val = int(num_str, 10)
            hex_str = f"{decimal_val:06X}"
            return f"ZR{hex_str}"

        return headdevice

    def _do_read(self, req) -> Any:
        """Execute a read on the worker thread. Never call from outside the worker."""
        if self.client is None:
            raise PLCConnectionError("Mitsubishi client not initialized")

        # Handle internal test_connection probe
        if isinstance(req, base._TestReq):
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
                # STRING: each 16-bit word register holds 2 ASCII characters.
                # 1 register = 2 chars, so register_count=10 reads up to 20 chars.
                reg_count = getattr(req, 'register_count', 10) or 10
                word_data = self.client.batchread_wordunits(headdevice, reg_count)

                # Try standard byte order (LE: low byte = 1st char)
                raw_le = self._words_to_bytes(word_data)
                text_le = raw_le.decode('ascii', errors='replace').split('\x00')[0]

                # Try swapped byte order (BE: high byte = 1st char)
                raw_be = self._words_to_bytes_swapped(word_data)
                text_be = raw_be.decode('ascii', errors='replace').split('\x00')[0]

                # Score each candidate: count printable ASCII chars (0x20-0x7E)
                def _printable_score(s: str) -> int:
                    return sum(1 for c in s if 0x20 <= ord(c) <= 0x7E) if s else 0

                score_le = _printable_score(text_le)
                score_be = _printable_score(text_be)

                # Pick the result with more printable characters
                if score_be > score_le:
                    logger.debug(
                        f"STRING {headdevice}: swapped byte order chosen "
                        f"(LE score={score_le}, BE score={score_be})"
                    )
                    return text_be
                return text_le

            elif req.data_type == DataType.WORD_ARRAY:
                reg_count = getattr(req, 'register_count', 10) or 10
                reg_count = min(reg_count, 32768)
                
                results = []
                current_device = headdevice
                remaining = reg_count
                
                while remaining > 0:
                    chunk = min(remaining, 960)
                    word_data = self.client.batchread_wordunits(current_device, chunk)
                    results.extend(word_data)
                    remaining -= chunk
                    if remaining > 0:
                        current_device = self._advance_headdevice(current_device, chunk)
                        
                return results

            elif req.data_type == DataType.BIT_ARRAY:
                reg_count = getattr(req, 'register_count', 10) or 10
                reg_count = min(reg_count, 32768)
                
                results = []
                current_device = headdevice
                remaining = reg_count
                
                while remaining > 0:
                    chunk = min(remaining, 7168)
                    bit_data = self.client.batchread_bitunits(current_device, chunk)
                    results.extend(bit_data)
                    remaining -= chunk
                    if remaining > 0:
                        current_device = self._advance_headdevice(current_device, chunk)
                        
                return results

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

            elif req.data_type == DataType.WORD_ARRAY:
                if not isinstance(req.value, list):
                    raise ValueError("WORD_ARRAY requires a list of integers")
                self.client.batchwrite_wordunits(headdevice, [int(v) & 0xFFFF for v in req.value])

            elif req.data_type == DataType.BIT_ARRAY:
                if not isinstance(req.value, list):
                    raise ValueError("BIT_ARRAY requires a list of integers (0 or 1)")
                self.client.batchwrite_bitunits(headdevice, [int(bool(v)) for v in req.value])

            else:
                self.client.batchwrite_wordunits(headdevice, [int(req.value)])

            return True
        except Exception as e:
            raise PLCWriteError(f"Mitsubishi write failed: {e}")


