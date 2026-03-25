# ABB PLC Integration

## Overview
The ABB PLC service uses **PyModbus** library to communicate with ABB PLCs over Modbus/TCP protocol. This is typically used with ABB's AC500 series or other Modbus-enabled controllers.

## Supported Controllers
- AC500 series (PM5xx, PM6xx)
- Controllers with Modbus/TCP server capability
- Generic Modbus/TCP devices

## Connection Parameters
```json
{
  "plc_type": "abb",
  "ip": "192.168.1.103",
  "port": 502
}
```

## Address Format
ABB uses Modbus addressing:
- `40001` - Holding register 1 (16-bit)
- `30001` - Input register 1 (16-bit)
- `00001` - Coil 1 (bit)
- `10001` - Discrete input 1 (bit)

## Data Types
- **BOOL**: Coil/Discrete input (bit)
- **INT**: Holding/Input register (16-bit signed)
- **DINT**: Two consecutive registers (32-bit signed)
- **REAL**: Two consecutive registers (32-bit float)
- **STRING**: Multiple registers (ASCII)

## Example Usage
```python
# Connect
POST /api/plc/connect
{
  "plc_type": "abb",
  "ip": "192.168.1.103",
  "port": 502
}

# Read data
POST /api/plc/read
{
  "ip": "192.168.1.103",
  "address": "40001",
  "data_type": "INT"
}

# Write data
POST /api/plc/write
{
  "ip": "192.168.1.103",
  "address": "40001",
  "data_type": "INT",
  "value": 4321
}
```

## Troubleshooting
- **Connection failed**: Verify PLC has Modbus/TCP enabled and correct port
- **Address errors**: Confirm register/coil numbers and data types
- **Communication issues**: Check Modbus configuration in PLC
- **ABB specific**: Ensure AC500 series has Modbus TCP server configured

## Getting Started with ABB PLCs
1. **PLC Setup**:
   - Configure IP address in Automation Builder
   - Enable Modbus TCP server in PLC configuration
   - Set up holding registers and coils for external access

2. **Software Setup**:
   ```bash
   git clone <repository-url>
   cd plc-diagnostics-bridge
   pip install -r backend/requirements.txt
   docker-compose up --build
   ```

3. **Testing Connection**:
   - Open web interface at http://localhost:8080
   - Select "abb" as PLC type
   - Enter PLC IP and port 502
   - Test connection and start monitoring

## Dependencies
- `pymodbus>=3.7.0`