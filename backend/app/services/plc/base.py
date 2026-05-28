import socket
import time
import json
import uuid
from abc import ABC, abstractmethod
from typing import Any
import threading
import queue
import logging
from enum import Enum
from app.schemas.plc import PLCConnectRequest, PLCReadRequest, PLCWriteRequest, DataType
from app.core.exceptions import PLCConnectionError, PLCReadError, PLCWriteError

logger = logging.getLogger(__name__)

# ─────────────────── Redis Connection (lazy singleton) ───────────────────

_redis_client = None
_redis_checked = False

def _get_redis():
    """Lazily connect to Redis. Returns None if unavailable."""
    global _redis_client, _redis_checked
    if _redis_checked:
        return _redis_client
    _redis_checked = True
    try:
        from app.core.config import settings
        url = getattr(settings, "REDIS_URL", "")
        if not url:
            logger.info("Redis disabled (REDIS_URL empty)")
            return None
        import redis as redis_lib
        _redis_client = redis_lib.Redis.from_url(url, decode_responses=True, socket_timeout=2)
        _redis_client.ping()
        logger.info(f"Redis connected: {url}")
    except Exception as e:
        logger.warning(f"Redis unavailable, falling back to threading queue: {e}")
        _redis_client = None
    return _redis_client


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

class _TestReq:
    """Lightweight sentinel for internal test_connection probes via the RPC queue."""
    pass


class BasePLCService(ABC):
    def __init__(self):
        self.is_connected = False
        self._op_queue: queue.Queue[_RPCRequest | None] = queue.Queue(maxsize=256)
        self._worker: threading.Thread | None = None
        self._lock = threading.Lock()
        self._redis = _get_redis()
        self._redis_queue_key: str | None = None  # set on _start_worker
        self._latency_ms: float = 0.0  # last operation round-trip time

    # ───────────────────── Worker Thread ─────────────────────

    def _start_worker(self, name: str):
        """Start the background worker that drains the operation queue."""
        if self._worker is not None and self._worker.is_alive():
            return
        # Ensure queue is fresh and empty
        self._op_queue = queue.Queue(maxsize=256)
        self._redis_queue_key = f"plcbridge:rpc:{name}"
        self._worker = threading.Thread(
            target=self._worker_loop,
            name=name,
            daemon=True,
        )
        self._worker.start()
        logger.info(f"RPC worker started: {name} (redis={'yes' if self._redis else 'no'})")

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
                    rpc.error = PLCConnectionError("Connection closed while request was pending")
                    rpc.done.set()
            except queue.Empty:
                break

    def _worker_loop(self):
        """Continuously dequeue and execute PLC operations one at a time."""
        while True:
            rpc = self._op_queue.get()
            if rpc is None:
                # Poison pill → exit
                break
            t0 = time.monotonic()
            try:
                if rpc.op == _OpType.READ:
                    rpc.result = self._do_read(rpc.req)
                elif rpc.op == _OpType.WRITE:
                    rpc.result = self._do_write(rpc.req)
            except Exception as e:
                rpc.error = e
            finally:
                self._latency_ms = round((time.monotonic() - t0) * 1000, 2)
                rpc.done.set()

    def _acquire_redis_lock(self, timeout: float = 10.0) -> bool:
        """Acquire a Redis-based distributed lock for this PLC endpoint."""
        if not self._redis or not self._redis_queue_key:
            return False
        lock_key = f"{self._redis_queue_key}:lock"
        try:
            # SET NX with expiry — atomic lock acquisition
            acquired = self._redis.set(lock_key, "1", nx=True, ex=int(timeout) + 2)
            return bool(acquired)
        except Exception:
            return False

    def _release_redis_lock(self):
        """Release the Redis distributed lock."""
        if not self._redis or not self._redis_queue_key:
            return
        lock_key = f"{self._redis_queue_key}:lock"
        try:
            self._redis.delete(lock_key)
        except Exception:
            pass

    def _enqueue(self, op: _OpType, req: Any, timeout: float = 10.0) -> Any:
        """
        Submit an operation to the RPC queue and block until it completes.
        This is the ONLY path through which read/write hits the socket.

        If Redis is available, a distributed lock is acquired first to prevent
        cross-worker collisions when uvicorn runs multiple processes.
        """
        if not self.is_connected:
            raise PLCConnectionError("PLC not connected")
        if self._worker is None or not self._worker.is_alive():
            self.is_connected = False
            raise PLCConnectionError("RPC worker is not running — reconnect required")

        # Distributed lock via Redis (cross-process safety)
        redis_locked = self._acquire_redis_lock(timeout)

        try:
            rpc = _RPCRequest(op, req)
            try:
                self._op_queue.put(rpc, timeout=2.0)
            except queue.Full:
                err_msg = "Operation queue full — PLC may be unresponsive"
                raise PLCReadError(err_msg) if op == _OpType.READ else PLCWriteError(err_msg)

            # Wait for the worker to execute our request
            if not rpc.done.wait(timeout=timeout):
                err_msg = "Operation timed out"
                raise PLCReadError(err_msg) if op == _OpType.READ else PLCWriteError(err_msg)

            if rpc.error is not None:
                raise rpc.error
            return rpc.result
        finally:
            if redis_locked:
                self._release_redis_lock()

    @abstractmethod
    def connect(self, req: PLCConnectRequest) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        pass

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

    def get_latency(self) -> float:
        """Return the last operation's round-trip latency in milliseconds."""
        return self._latency_ms

    def check_port_busy(self, ip: str, port: int) -> dict:
        """
        Check port status on the given IP address.
        Returns detailed status information.
        """
        result = {
            'busy': False,
            'status': 'unknown',
            'message': '',
            'response_time': None
        }
        
        try:
            start_time = time.time()
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            connect_result = sock.connect_ex((ip, port))
            response_time = time.time() - start_time
            
            sock.close()
            
            result['response_time'] = round(response_time * 1000, 2)  # ms
            
            if connect_result == 0:
                result['busy'] = True
                result['status'] = 'open'
                result['message'] = f'Port {port} is open and accepting connections'
            else:
                result['busy'] = False
                result['status'] = 'closed'
                result['message'] = f'Port {port} is closed or filtered'
                
        except socket.timeout:
            result['status'] = 'timeout'
            result['message'] = f'Port {port} check timed out'
        except socket.gaierror:
            result['status'] = 'dns_error'
            result['message'] = f'Invalid IP address: {ip}'
        except Exception as e:
            result['status'] = 'error'
            result['message'] = f'Port check failed: {str(e)}'
        
        return result

    def read(self, req: PLCReadRequest) -> Any:
        return self._enqueue(_OpType.READ, req)

    def write(self, req: PLCWriteRequest) -> bool:
        return self._enqueue(_OpType.WRITE, req)

    @abstractmethod
    def _do_read(self, req: Any) -> Any:
        pass

    @abstractmethod
    def _do_write(self, req: PLCWriteRequest) -> bool:
        pass
