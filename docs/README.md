# PLC Integration Documentation

This directory contains detailed documentation for each supported PLC brand and protocol.

## Supported PLC Brands

### Siemens
- **Protocol**: S7 (ISO-on-TCP)
- **Library**: python-snap7
- **Documentation**: [Siemens PLC Integration](siemens.md)
- **Data Types**: Bool, Int, DInt, Real, String

### Mitsubishi
- **Protocol**: MC Protocol (MELSEC)
- **Library**: pymcprotocol
- **Documentation**: [Mitsubishi PLC Integration](mitsubishi.md)
- **Data Types**: Bool, Int, DInt, Real, String

### Rockwell (Allen-Bradley)
- **Protocol**: EtherNet/IP (CIP)
- **Library**: pylogix
- **Documentation**: [Rockwell PLC Integration](rockwell.md)
- **Data Types**: Bool, Int, DInt, Real, String

### ABB
- **Protocol**: Modbus/TCP
- **Library**: pymodbus
- **Documentation**: [ABB PLC Integration](abb.md)
- **Data Types**: Bool, Int, DInt, Real, String

### Fanuc
- **Protocol**: Custom FTP-based
- **Library**: fxvrlib (custom)
- **Documentation**: [Fanuc Robot Controller Integration](fanuc.md)
- **Data Types**: Float (preset values)

## Common API Usage

All PLC types use the same REST API endpoints:

### Connect
```http
POST /api/plc/connect
Content-Type: application/json

{
  "plc_type": "siemens",
  "ip": "192.168.1.100",
  "port": 102,
  "rack": 0,
  "slot": 1
}
```

### Read Data
```http
POST /api/plc/read
Content-Type: application/json

{
  "ip": "192.168.1.100",
  "address": "DB1.DBW0",
  "data_type": "INT"
}
```

### Write Data
```http
POST /api/plc/write
Content-Type: application/json

{
  "ip": "192.168.1.100",
  "address": "DB1.DBW0",
  "data_type": "INT",
  "value": 1234
}
```

## Getting Started

1. Start the application with Docker:
   ```bash
   docker-compose up -d
   ```

2. Access the web interface at http://localhost:8080

3. Use the API at http://localhost:8000/docs

## Troubleshooting

- Check the [main README](../README.md) for general setup
- Refer to specific PLC documentation for protocol details
- View application logs: `docker-compose logs backend`

## Contributing

When adding support for new PLC brands:
1. Create a new service class in `backend/app/services/plc/`
2. Update the factory in `factory.py`
3. Add documentation in this directory
4. Update the main README table