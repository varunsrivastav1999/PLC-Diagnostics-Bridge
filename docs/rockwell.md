# Rockwell PLC Integration

## Overview
The Rockwell PLC service uses the **PyLogix** library to communicate with Allen-Bradley/Logix controllers over EtherNet/IP protocol.

## Supported Controllers
- ControlLogix (1756 series)
- CompactLogix (1769 series)
- MicroLogix (1100, 1400)
- SLC 500 (with Ethernet)

## Connection Parameters
```json
{
  "plc_type": "rockwell",
  "ip": "192.168.1.102",
  "port": 44818,
  "slot": 0
}
```

## Address Format
Rockwell uses tag-based addressing:
- `MyTag` - User-defined tag
- `MyTag[0]` - Array element
- `MyTag.MyMember` - UDT member
- `Local:1:I.Data[0]` - I/O module data

## Data Types
- **BOOL**: Boolean values
- **INT**: 16-bit signed integer
- **DINT**: 32-bit signed integer
- **REAL**: 32-bit IEEE 754 float
- **STRING**: ASCII string

## Example Usage
```python
# Connect
POST /api/plc/connect
{
  "plc_type": "rockwell",
  "ip": "192.168.1.102",
  "slot": 0
}

# Read data
POST /api/plc/read
{
  "ip": "192.168.1.102",
  "address": "MyIntegerTag",
  "data_type": "INT"
}

# Write data
POST /api/plc/write
{
  "ip": "192.168.1.102",
  "address": "MyIntegerTag",
  "data_type": "INT",
  "value": 9999
}
```

## Troubleshooting
- **Connection failed**: Check IP address and slot number (0 for CompactLogix, slot number for ControlLogix)
- **Tag not found**: Verify tag exists and is not aliased
- **Permission errors**: Ensure controller allows external connections
- **Rockwell specific**: Confirm EtherNet/IP is enabled and RSLinx is not blocking connections

## Getting Started with Rockwell PLCs
1. **PLC Setup**:
   - Configure IP address in Logix Designer
   - Enable EtherNet/IP communication
   - Create controller tags for external access

2. **Software Setup**:
   ```bash
   git clone <repository-url>
   cd plc-diagnostics-bridge
   pip install -r backend/requirements.txt
   docker-compose up --build
   ```

3. **Testing Connection**:
   - Open web interface at http://localhost:8080
   - Select "rockwell" as PLC type
   - Enter PLC IP (port 44818 default) and slot number
   - Test connection and start monitoring

## Dependencies
- `pylogix>=1.1.5`