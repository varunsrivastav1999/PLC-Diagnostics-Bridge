# Mitsubishi PLC Integration

## Overview
The Mitsubishi PLC service uses the **MC Protocol** (MELSEC Communication Protocol) for Ethernet communication with Mitsubishi PLCs.

## Supported Controllers
- Q Series (Q00, Q01, Q02, Q06, Q12, Q25)
- L Series (L02, L06, L26)
- FX Series (FX3U, FX3G, FX5U) with Ethernet module

## Connection Parameters
```json
{
  "plc_type": "mitsubishi",
  "ip": "192.168.1.101",
  "port": 5000
}
```

## Address Format
Mitsubishi uses device addressing:
- `D0` - Data register D0 (16-bit)
- `M0` - Internal relay M0 (bit)
- `X0` - Input X0 (bit)
- `Y0` - Output Y0 (bit)
- `R0` - File register R0 (16-bit)

## Data Types
- **BOOL**: Bit devices (M, X, Y, etc.)
- **INT**: 16-bit signed integer (D, R registers)
- **DINT**: 32-bit signed integer (two consecutive registers)
- **REAL**: 32-bit IEEE 754 float (two consecutive registers)
- **STRING**: ASCII string in consecutive registers

## Example Usage
```python
# Connect
POST /api/plc/connect
{
  "plc_type": "mitsubishi",
  "ip": "192.168.1.101",
  "port": 5000
}

# Read data
POST /api/plc/read
{
  "ip": "192.168.1.101",
  "address": "D0",
  "data_type": "INT"
}

# Write data
POST /api/plc/write
{
  "ip": "192.168.1.101",
  "address": "D0",
  "data_type": "INT",
  "value": 5678
}
```

## Troubleshooting
- **Connection failed**: Verify PLC has Ethernet module and MC protocol enabled
- **Port issues**: Default port is 5000, confirm PLC configuration
- **Address errors**: Check device type and number ranges for your PLC model

## Dependencies
- `pymcprotocol>=0.3.0`