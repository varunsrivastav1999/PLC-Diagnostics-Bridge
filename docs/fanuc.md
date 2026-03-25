# Fanuc Robot Controller Integration

## Overview
The Fanuc PLC service uses the custom **fxvrlib** library to communicate with Fanuc Paint Robot controllers via FTP for preset management.

## Supported Controllers
- Fanuc Paint Robots with V9.x software
- Controllers with FTP server enabled
- Preset management capability

## Connection Parameters
```json
{
  "plc_type": "fanuc",
  "ip": "192.168.1.104",
  "port": 21
}
```

## Address Format
Fanuc uses structured preset addressing:
- `1,1,BELL` - Job 1, Color 1, BELL presets
- `1,1,BELL,1` - Job 1, Color 1, BELL preset 1
- `1,1,BELL,1,fluid_rate` - Job 1, Color 1, BELL preset 1, fluid_rate value

## Preset Types
- **BELL**: Bell/bell parameters (fluid_rate, bell_speed, shape_air1, estat_KV, shape_air2)
- **GUN**: Gun parameters (fluid_rate, atom_air, fan_air, estat_KV)

## Data Types
- **FLOAT**: All preset values are 32-bit floats
- **INT**: Job and color numbers are integers

## Example Usage
```python
# Connect
POST /api/plc/connect
{
  "plc_type": "fanuc",
  "ip": "192.168.1.104",
  "port": 21
}

# Read all BELL presets for job 1, color 1
POST /api/plc/read
{
  "ip": "192.168.1.104",
  "address": "1,1,BELL",
  "data_type": "STRING"
}

# Read specific preset value
POST /api/plc/read
{
  "ip": "192.168.1.104",
  "address": "1,1,BELL,1,fluid_rate",
  "data_type": "REAL"
}

# Write preset value
POST /api/plc/write
{
  "ip": "192.168.1.104",
  "address": "1,1,BELL,1,fluid_rate",
  "data_type": "REAL",
  "value": 2.5
}
```

## Troubleshooting
- **FTP connection failed**: Verify FTP is enabled on robot controller
- **Authentication errors**: Check username/password (default: guest/guest)
- **Preset read/write errors**: Confirm job/color numbers exist
- **Fanuc specific**: Ensure robot controller has preset management enabled

## Getting Started with Fanuc Robots
1. **Robot Setup**:
   - Enable FTP server in robot controller settings
   - Configure IP address and network settings
   - Create paint jobs and color configurations

2. **Software Setup**:
   ```bash
   git clone <repository-url>
   cd plc-diagnostics-bridge
   pip install -r backend/requirements.txt
   docker-compose up --build
   ```

3. **Testing Connection**:
   - Open web interface at http://localhost:8080
   - Select "fanuc" as PLC type
   - Enter robot controller IP and port 21
   - Test connection and start monitoring presets

## Dependencies
- Custom `fxvrlib` library (included)
- FTP client for file transfer

## Notes
- Requires FTP server enabled on Fanuc controller
- Preset data is stored in XVR files on controller
- Supports up to 20 presets per color per job