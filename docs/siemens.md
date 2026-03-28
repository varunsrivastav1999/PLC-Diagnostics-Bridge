# Siemens PLC Integration

## Overview
The Siemens PLC service uses the **Snap7** library to communicate with Siemens S7 PLCs over ISO-on-TCP protocol.

## Supported Controllers
- S7-300, S7-400, S7-1200, S7-1500
- CPU models with Ethernet interface

## Connection Parameters
```json
{
  "plc_type": "siemens",
  "ip": "192.168.1.100",
  "port": 102,
  "rack": 0,
  "slot": 1,
  "cpu_type": "S7-1200"
}
```

## Address Format
Siemens uses DB (Data Block) addressing:
- `DB1.DBX0.0` - Bool at DB1, byte 0, bit 0
- `DB1.DBB1` - Byte-based start offset, commonly used for strings
- `DB1.DBW2` - Word (16-bit) at DB1, byte 2
- `DB1.DBD4` - Double word (32-bit) at DB1, byte 4

## Data Types
- **BOOL**: Single bit values
- **INT**: 16-bit signed integer
- **DINT**: 32-bit signed integer
- **REAL**: 32-bit IEEE 754 float
- **STRING**: ASCII string with length prefix

## Example Usage
```python
# Connect
POST /api/plc/connect
{
  "plc_type": "siemens",
  "ip": "192.168.1.100",
  "rack": 0,
  "slot": 1
}

# Read data
POST /api/plc/read
{
  "ip": "192.168.1.100",
  "address": "DB1.DBW0",
  "data_type": "INT"
}

# Write data
POST /api/plc/write
{
  "ip": "192.168.1.100",
  "address": "DB1.DBW0",
  "data_type": "INT",
  "value": 1234
}
```

## Troubleshooting
- **Connection failed**: Check IP address, rack/slot configuration
- **Read/write errors**: Verify DB exists and address matches the data type. `BOOL` must use `DBX...`, while numeric and string operations must not use `DBX...`
- **Timeout**: Increase `CONNECTION_TIMEOUT_SEC` in environment
- **Siemens specific**: Ensure PLC is in RUN mode and PUT/GET communication is enabled

## Getting Started with Siemens PLCs
1. **PLC Setup**:
   - Configure IP address in TIA Portal
   - Enable PUT/GET communication in PLC properties
   - Set protection level to allow external access

2. **Software Setup**:
   ```bash
   git clone <repository-url>
   cd plc-diagnostics-bridge
   pip install -r backend/requirements.txt
   docker-compose up --build
   ```

3. **Testing Connection**:
   - Open web interface at http://localhost:8080
   - Select "siemens" as PLC type
   - Enter PLC IP, rack (0), slot (1 for S7-1200/1500)
   - Test connection and start monitoring

## Dependencies
- `python-snap7>=2.0.0`
- System: `libsnap7-dev` (installed in Docker)
