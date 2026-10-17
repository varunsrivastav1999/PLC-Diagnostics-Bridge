from __future__ import annotations

import asyncio
import logging
import threading
from typing import Any

from app.core.exceptions import PLCConnectionError, PLCReadError, PLCWriteError
from app.schemas.plc import DataType, PLCConnectRequest, PLCReadRequest, PLCWriteRequest
from app.services.plc.base import BasePLCService

logger = logging.getLogger(__name__)


class OPCUAPLCService(BasePLCService):
    """
    Industrial OPC-UA (IEC 62541) client service using asyncua.
    Provides standard SCADA-style communication with PLCs and industrial PC servers
    supporting OPC Unified Architecture.
    """

    def __init__(self):
        super().__init__()
        self.client: Any = None
        self._url: str = ""
        self._loop: asyncio.AbstractEventLoop | None = None
        self._loop_thread: threading.Thread | None = None

    def _start_loop(self) -> None:
        """Ensure a dedicated event loop thread is running for asyncua operations."""
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
            self._loop_thread = threading.Thread(
                target=self._loop.run_forever,
                name=f"opcua-loop-{id(self)}",
                daemon=True,
            )
            self._loop_thread.start()

    def _stop_loop(self) -> None:
        """Safely stop and close the event loop thread."""
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._loop_thread and self._loop_thread.is_alive():
            self._loop_thread.join(timeout=2.0)
        if self._loop and not self._loop.is_closed():
            self._loop.close()
        self._loop = None
        self._loop_thread = None

    def _run_async(self, coro, timeout: float = 10.0) -> Any:
        """Execute an async coroutine on the dedicated event loop."""
        if self._loop is None or self._loop.is_closed():
            raise PLCConnectionError("OPC-UA event loop is not active")
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            raise PLCConnectionError(f"OPC-UA operation timed out after {timeout}s")
        except Exception as e:
            raise e

    def _build_endpoint_url(self, ip: str, port: int | None) -> str:
        """Construct standard opc.tcp endpoint URL."""
        clean_ip = ip.strip()
        if clean_ip.startswith("opc.tcp://"):
            return clean_ip
        target_port = port if port is not None else 4840
        return f"opc.tcp://{clean_ip}:{target_port}"

    def connect(self, req: PLCConnectRequest) -> bool:
        try:
            from asyncua import Client

            self._url = self._build_endpoint_url(req.ip, req.port)
            self._start_loop()

            async def _do_connect():
                client = Client(url=self._url, timeout=5)
                await client.connect()
                return client

            self.client = self._run_async(_do_connect(), timeout=7.0)
            self.is_connected = True
            target_port = req.port if req.port is not None else 4840
            self._start_worker(f"opcua-{req.ip}:{target_port}")
            logger.info(f"OPC-UA connected successfully: {self._url}")
            return True
        except Exception as e:
            self.is_connected = False
            self._stop_loop()
            logger.error(f"OPC-UA connection failed for {req.ip}: {e}")
            raise PLCConnectionError(f"OPC-UA connection failed: {e}")

    def disconnect(self) -> bool:
        try:
            self._stop_worker()
            if self.client and self._loop and not self._loop.is_closed():
                async def _do_disconnect():
                    try:
                        await self.client.disconnect()
                    except Exception:
                        pass

                try:
                    self._run_async(_do_disconnect(), timeout=3.0)
                except Exception:
                    pass
        finally:
            self._stop_loop()
            self.client = None
            self.is_connected = False
        return True

    def test_connection(self) -> bool:
        if not self.is_connected or not self.client:
            return False
        try:
            from asyncua import ua

            async def _check():
                # Read ServerStatus CurrentTime or Root NodeId to verify link
                root = self.client.nodes.root
                await root.read_attribute(ua.AttributeIds.NodeId)
                return True

            return bool(self._run_async(_check(), timeout=3.0))
        except Exception:
            self.is_connected = False
            return False

    def _do_read(self, req: PLCReadRequest) -> Any:
        try:
            async def _read():
                node = self.client.get_node(req.address)
                return await node.read_value()

            raw_val = self._run_async(_read(), timeout=6.0)

            # Type conversion
            if req.data_type == DataType.BOOL:
                if isinstance(raw_val, bool):
                    return raw_val
                if isinstance(raw_val, (int, float)):
                    return bool(raw_val)
                return str(raw_val).strip().lower() in ("true", "1", "t", "yes", "on")

            if req.data_type == DataType.INT:
                return int(raw_val) if raw_val is not None else 0

            if req.data_type == DataType.DINT:
                return int(raw_val) if raw_val is not None else 0

            if req.data_type in (DataType.REAL, DataType.FLOAT):
                return round(float(raw_val), 6) if raw_val is not None else 0.0

            if req.data_type == DataType.STRING:
                return str(raw_val) if raw_val is not None else ""

            return raw_val
        except PLCReadError:
            raise
        except Exception as e:
            raise PLCReadError(f"OPC-UA read failed on [{req.address}]: {e}")

    def _do_write(self, req: PLCWriteRequest) -> bool:
        try:
            from asyncua import ua

            val = req.value
            dt = req.data_type

            if dt == DataType.BOOL:
                bool_val = bool(str(val).lower() in ("true", "1", "t", "yes", "on")) if isinstance(val, str) else bool(val)
                variant = ua.Variant(bool_val, ua.VariantType.Boolean)
            elif dt == DataType.INT:
                variant = ua.Variant(int(val), ua.VariantType.Int16)
            elif dt == DataType.DINT:
                variant = ua.Variant(int(val), ua.VariantType.Int32)
            elif dt in (DataType.REAL, DataType.FLOAT):
                variant = ua.Variant(float(val), ua.VariantType.Float)
            elif dt == DataType.STRING:
                variant = ua.Variant(str(val), ua.VariantType.String)
            else:
                variant = ua.Variant(val)

            async def _write():
                node = self.client.get_node(req.address)
                await node.write_value(variant)
                return True

            self._run_async(_write(), timeout=6.0)
            return True
        except PLCWriteError:
            raise
        except Exception as e:
            raise PLCWriteError(f"OPC-UA write failed on [{req.address}]: {e}")
