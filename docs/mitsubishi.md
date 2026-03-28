# Mitsubishi PLC Integration

## Overview
The Mitsubishi PLC service uses the **MC Protocol** (MELSEC Communication Protocol) for Ethernet communication with Mitsubishi PLCs.

## Supported Controllers
- Q Series (Q00, Q01, Q02, Q06, Q12, Q25)
- L Series (L02, L06, L26)
- FX Series (FX3U, FX3G, FX5U) with Ethernet module
  - **FX5U-500B**: High-performance compact PLC with built-in Ethernet
  - **FX5U-800B**: Extended I/O capacity model
  - **FX5U-320B**: Standard performance model

## FX5U-500B Specific Features
The FX5U-500B is a high-performance compact PLC that includes:
- Built-in Ethernet port (default port 5000)
- High-speed processing (28ns per basic instruction)
- Large program capacity (64k steps)
- Advanced positioning control
- Built-in analog I/O capabilities
- SD card slot for program backup and data logging

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
- `ZR0` - Extended file register ZR0 (word device)
- `M0` - Internal relay M0 (bit)
- `X0` - Input X0 (bit)
- `Y0` - Output Y0 (bit)
- `R0` - File register R0 (16-bit)

## Data Types
- **BOOL**: Bit devices (M, X, Y, etc.)
- **INT**: 16-bit signed integer (D, R, ZR registers)
- **DINT**: 32-bit signed integer (two consecutive registers)
- **REAL**: 32-bit IEEE 754 float (two consecutive registers)
- **STRING**: ASCII string in consecutive registers

`ZR` is an address/tag prefix, not a separate `data_type`. Use `INT`, `DINT`, `REAL`, `FLOAT`, or `STRING` with a `ZR...` address.

## Example Usage
```python
# Connect to FX5U-500B
POST /api/plc/connect
{
  "plc_type": "mitsubishi",
  "ip": "192.168.1.101",
  "port": 5000
}

# Read data from FX5U-500B
POST /api/plc/read
{
  "ip": "192.168.1.101",
  "address": "ZR100",
  "data_type": "INT"
}

# Write data to FX5U-500B
POST /api/plc/write
{
  "ip": "192.168.1.101",
  "address": "ZR100",
  "data_type": "INT",
  "value": 5678
}
```

## FX5U-500B Configuration
To use this application with FX5U-500B:

1. **PLC Setup**:
   - Ensure Ethernet communication is enabled
   - Set IP address in PLC parameter settings
   - Enable MC Protocol (MELSEC Communication Protocol)
   - Default port: 5000

2. **GX Works3 Software**:
   - Use GX Works3 for programming
   - Configure Ethernet settings in PLC parameters
   - Set communication protocol to "MC Protocol"

3. **Application Usage**:
   - Clone this repository
   - Install dependencies: `pip install -r requirements.txt`
   - Start the application: `docker-compose up`
   - Use the web interface or REST API to connect

## Performance Characteristics
- **Scan Time**: ~1-5ms depending on program size
- **Communication Speed**: Up to 10Mbps Ethernet
- **Data Transfer**: Optimized for real-time industrial applications
- **Reliability**: Built-in error checking and recovery mechanisms

## Troubleshooting
- **Connection failed**: Verify PLC has Ethernet module and MC protocol enabled
- **Port issues**: Default port is 5000, confirm PLC configuration
- **Address errors**: Check device type and number ranges for your PLC model
- **FX5U-500B specific**:
  - Ensure PLC is in RUN mode
  - Check Ethernet cable connection
  - Verify IP address configuration in GX Works3
  - Confirm MC Protocol is enabled in PLC parameters

## Dependencies
- `pymcprotocol>=0.3.0`
- Python 3.8+
- GX Works3 (for PLC programming and configuration)

## Getting Started with FX5U-500B
1. **Hardware Setup**:
   - Connect FX5U-500B to your network
   - Power on the PLC
   - Use GX Works3 to set IP address and enable MC Protocol

2. **Software Setup**:
   ```bash
   git clone <repository-url>
   cd plc-diagnostics-bridge
   pip install -r backend/requirements.txt
   docker-compose up --build
   ```

3. **Testing Connection**:
   - Open web interface at http://localhost:8080
   - Select "mitsubishi" as PLC type
   - Enter PLC IP address and port 5000
   - Test connection and start monitoring
