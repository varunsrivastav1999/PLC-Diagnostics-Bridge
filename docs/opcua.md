# OPC-UA Protocol Integration (IEC 62541)

The **PLC Diagnostics Bridge** supports industrial communication over **OPC Unified Architecture (OPC-UA)** via the high-performance `asyncua` asynchronous client engine.

---

## 🔌 Connection Setup

- **Default Port**: `4840` (`opc.tcp://<host>:4840`)
- **Protocol**: Binary TCP (`opc.tcp`)
- **Endpoint URL**: Accepts IP (e.g. `192.168.1.50`), IP with custom port, or full OPC-UA endpoint URI (e.g. `opc.tcp://192.168.1.50:4840/freeopcua/server/`).

---

## 🏷️ NodeId & Addressing Syntax

OPC-UA uses standard **NodeId** syntax strings:

| Syntax Format | Description | Example |
|---|---|---|
| `ns=<index>;s=<string>` | String Identifier | `ns=2;s=Channel1.Device1.Temperature` |
| `ns=<index>;i=<integer>` | Numeric Identifier | `ns=2;i=1001` |
| `i=<integer>` | Root / System Numeric NodeId | `i=2258` (Current Server Time) |
| `ns=<index>;g=<guid>` | GUID Identifier | `ns=2;g=12345678-1234-1234-1234-123456789abc` |

---

## 📊 Supported Data Types

- **`BOOL`** — Boolean True / False
- **`INT`** — 16-bit Integer (`Int16` / `UInt16`)
- **`DINT`** — 32-bit Integer (`Int32` / `UInt32`)
- **`REAL` / `FLOAT`** — 32-bit Single-Precision Float
- **`STRING`** — UTF-8 / ASCII Character String

---

## 🐍 Python SDK Example

```python
from plcbridge_sdk import PLCManager, ConnectionParams, ReadParams, WriteParams, DataType

manager = PLCManager()

# 1. Connect
manager.connect(ConnectionParams(
    plc_type="opcua",
    ip="192.168.1.50",
    port=4840
))

# 2. Read Variable
val = manager.read(ReadParams(
    plc_type="opcua",
    ip="192.168.1.50",
    port=4840,
    data_type=DataType.REAL,
    address="ns=2;s=Line1.TankLevel"
))
print("Tank Level:", val)

# 3. Write Variable
manager.write(WriteParams(
    plc_type="opcua",
    ip="192.168.1.50",
    port=4840,
    data_type=DataType.BOOL,
    address="ns=2;s=Line1.PumpRunning",
    value=True
))
```
