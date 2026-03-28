<p align="center">
  <img src="frontend/public/favicon.png" alt="PLC Diagnostics Bridge" width="80" />
</p>

<h1 align="center">PLC Diagnostics Bridge</h1>

<p align="center">
  <strong>A production-ready, dockerized diagnostic tool for industrial PLC communication testing.</strong><br/>
  Real-time read &amp; write support for Siemens · Rockwell · Mitsubishi · ABB · Fanuc
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Vue%203-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white" alt="Vue 3" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/TailwindCSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="TailwindCSS" />
</p>

---

## 📋 Overview

**PLC Diagnostics Bridge** is a full-stack web application that provides a unified SCADA-style interface for testing and diagnosing communication with multiple industrial PLC brands. It enables engineers to **connect**, **read**, and **write** data (Bool, Int, Float, String, etc.) across different protocols from a single dashboard.

## 🏗️ Architecture

```
┌─────────────────────────────┐
│       Vue 3 Frontend        │
│   PrimeVue · TailwindCSS    │
│        (Nginx :80)          │
└─────────────┬───────────────┘
              │ HTTP / REST
┌─────────────▼───────────────┐
│      FastAPI  Backend       │
│       (Uvicorn :8000)       │
├─────────────────────────────┤
│    PLC Service  Layer       │
│  ┌─────────┬──────────┐     │
│  │ Siemens │ Rockwell │     │
│  │ (Snap7) │ (Pylogix)│     │
│  ├─────────┼──────────┤     │
│  │Mitsubish│   ABB    │     │
│  │(MCProto)│ (Modbus) │     │
│  ├─────────┼──────────┤     │
│  │  Fanuc  │  (more)  │     │
│  └─────────┴──────────┘     │
└─────────────────────────────┘
```

## ✨ Features

- 🔌 **Multi-PLC Support** — Siemens (S7), Rockwell (CIP), Mitsubishi (MC Protocol, including FX5U-500B), ABB (Modbus/TCP), Fanuc
- 📖 **Read & Write** — Bool, Int, DInt, Real/Float, String data types
- 🩺 **Connection Diagnostics** — Health checks, connection pooling, timeout management
- 🖥️ **Responsive Operations UI** — Desktop, tablet, and mobile-ready dashboard with internal scrolling and compact workspace summaries
- 📱 **Installable Mobile App Experience** — PWA manifest, service worker, and home-screen support for iPhone and Android
- 📦 **Reusable Python SDK** — `plcbridge-sdk` manager layer for custom SCADA websites, scripts, and backend services
- 🐳 **Fully Dockerized** — Single `docker-compose up` deployment
- ⚡ **Production Hardened** — Structured logging, global exception handling, resource limits

## 🚀 Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)

### Run

```bash
# Clone the repository
git clone https://github.com/<your-username>/plc-diagnostics-bridge.git
cd plc-diagnostics-bridge

# Start all services
docker-compose up --build
```

| Service  | URL                    |
|----------|------------------------|
| Frontend | http://localhost:8080   |
| Backend  | http://localhost:8000   |
| API Docs | http://localhost:8000/docs |

### Development (without Docker)

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## 📦 Use As A Python Library

The backend now exposes a reusable package at `backend/plcbridge_sdk` so you can build your own SCADA dashboard, script runner, or automation service on top of the same PLC communication layer.

### Install In Editable Mode

```bash
cd backend
pip install -e .
```

### Example

```python
from plcbridge_sdk import PLCManager, ConnectionParams, ReadParams, WriteParams, DataType

manager = PLCManager()

manager.connect(ConnectionParams(
    plc_type="siemens",
    ip="192.168.0.10",
    port=102,
    rack=0,
    slot=1,
))

value = manager.read(ReadParams(
    plc_type="siemens",
    ip="192.168.0.10",
    port=102,
    data_type=DataType.INT,
    address="DB1.DBW2",
))

manager.write(WriteParams(
    plc_type="siemens",
    ip="192.168.0.10",
    port=102,
    data_type=DataType.INT,
    address="DB1.DBW2",
    value=123,
))
```

### Register A Custom Driver

```python
from plcbridge_sdk import PLCManager, BasePLCService

class MyCustomPLC(BasePLCService):
    def connect(self, req): ...
    def disconnect(self): ...
    def test_connection(self): ...
    def read(self, req): ...
    def write(self, req): ...

PLCManager.register_driver("myplc", MyCustomPLC)
```

## 📱 Mobile And Tablet Use

The frontend now supports:

- **Desktop web** — full dashboard layout with fixed control rail and live operations workspace
- **Tablet web** — stacked layout with scroll-safe cards and touch-friendly spacing
- **Phone web** — compact workspace summary, full-page scrolling, and touch-friendly inputs
- **Installable mobile app** — add the PWA to the home screen on iPhone and Android

### Run On A Phone Or Tablet

For local testing on the same Wi-Fi network:

1. Start the backend on your computer.
2. Start the frontend with `npm run dev -- --host 0.0.0.0` inside `frontend/`.
3. Find your computer's local IP address, for example `192.168.0.25`.
4. Open `http://<your-computer-ip>:5173` on the phone or tablet browser.

For Docker deployments on the same network:

1. Start the stack with `docker-compose up --build`.
2. Open `http://<your-computer-ip>:8080` on the phone or tablet browser.

### Install On iPhone

1. Open the deployed app in Safari.
2. Tap **Share**.
3. Choose **Add to Home Screen**.
4. Launch it from the home screen as a standalone app.

### Install On Android

1. Open the deployed app in Chrome.
2. Tap the browser menu.
3. Choose **Install app** or **Add to Home screen**.
4. Launch it from the home screen as a standalone app.

### Mobile App Files

- `frontend/public/manifest.webmanifest` — install metadata
- `frontend/public/sw.js` — service worker shell caching
- `frontend/public/apple-touch-icon.png` — iPhone home-screen icon
- `frontend/public/icon-192.png` — Android/PWA icon
- `frontend/public/icon-512.png` — large install icon

## 📁 Project Structure

```
plc-diagnostics-bridge/
├── docker-compose.yml          # Orchestration
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml         # SDK packaging metadata
│   ├── requirements.txt
│   ├── plcbridge_sdk/         # Reusable Python SDK
│   └── app/
│       ├── main.py             # FastAPI entrypoint
│       ├── api/                # Route handlers
│       ├── core/               # Config & exceptions
│       ├── schemas/            # Pydantic models
│       ├── services/plc/       # PLC protocol drivers
│       │   ├── base.py         # Abstract base service
│       │   ├── factory.py      # Service factory
│       │   ├── siemens.py      # Snap7 driver
│       │   ├── rockwell.py     # Pylogix driver
│       │   ├── mitsubishi.py   # MC Protocol driver
│       │   ├── abb.py          # Modbus/TCP driver
│       │   └── fanuc.py        # Fanuc driver
│       ├── tests/              # Pytest suite
│       └── utils/              # Helpers
└── frontend/
    ├── Dockerfile
    ├── nginx.conf              # Production proxy config
    ├── index.html
    ├── public/
    │   ├── manifest.webmanifest
    │   ├── sw.js
    │   ├── apple-touch-icon.png
    │   ├── icon-192.png
    │   └── icon-512.png
    └── src/                    # Vue 3 application
```

## ⚙️ Configuration

Environment variables (set in `docker-compose.yml`):

| Variable               | Default                  | Description                    |
|------------------------|--------------------------|--------------------------------|
| `PROJECT_NAME`         | PLC Diagnostics Bridge   | Application name               |
| `VERSION`              | 2.0.0                    | App version                    |
| `DEBUG`                | false                    | Enable debug logging           |
| `CORS_ORIGINS`         | *                        | Allowed CORS origins           |
| `CONNECTION_TIMEOUT_SEC` | 5                      | PLC connection timeout (sec)   |
| `MAX_CONNECTIONS`      | 20                       | Max concurrent PLC connections |

## 🧭 Frontend Notes

- The live connection summary is rendered directly in the workspace strip, so the main operations view stays compact on smaller screens.
- The connection panel scrolls internally on shorter displays to prevent the UI from overflowing the viewport.
- The connection action area uses a single primary connect or disconnect button to keep the control rail compact on hosted screens.
- The frontend registers `frontend/public/sw.js` automatically when the browser supports service workers.
- For the best iPhone and Android experience, deploy the app over HTTPS.

## 🛡️ Supported PLC Protocols

| Brand      | Protocol        | Library         | Data Types                    | Docs |
|------------|-----------------|-----------------|-------------------------------|------|
| Siemens    | S7 (ISO-on-TCP) | python-snap7    | Bool, Int, DInt, Real, String | [📖](docs/siemens.md) |
| Rockwell   | CIP / EtherNet/IP | pylogix       | Bool, Int, Float, String      | [📖](docs/rockwell.md) |
| Mitsubishi | MC Protocol     | pymcprotocol    | Bool, Int, Float, String (FX5U-500B, Q/L Series) | [📖](docs/mitsubishi.md) |
| ABB        | Modbus/TCP      | pymodbus        | Bool, Int, Float, String      | [📖](docs/abb.md) |
| Fanuc      | Custom          | —               | Read/Write                    | [📖](docs/fanuc.md) |

📚 **Detailed documentation for each PLC brand**: [docs/](docs/)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

The Fanuc fxvrlib component is © FANUC America Corporation and licensed under Apache 2.0.

## 🌟 Support

- 📖 [Documentation](https://github.com/yourusername/plc-diagnostics-bridge/wiki)
- 🐛 [Issues](https://github.com/yourusername/plc-diagnostics-bridge/issues)
- 💬 [Discussions](https://github.com/yourusername/plc-diagnostics-bridge/discussions)

## 🙏 Acknowledgments

- FANUC Corporation for the fxvrlib library
- Open source community for the amazing libraries used
- Industrial automation engineers who inspired this project

---

<p align="center">Built for industrial automation engineers 🏭</p>
