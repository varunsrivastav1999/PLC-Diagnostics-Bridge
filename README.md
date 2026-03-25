<p align="center">
  <img src="frontend/public/favicon.png" alt="PLC Diagnostics Bridge" width="80" />
</p>

<h1 align="center">PLC Diagnostics Bridge</h1>

<p align="center">
  <strong>A production-ready, dockerized diagnostic tool for industrial PLC communication testing.</strong><br/>
  Real-time read &amp; write support for Siemens · Rockwell · Mitsubishi · ABB · Fanuc
</p>

<p align="center">
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
│  ┌─────────┬──────────┐    │
│  │ Siemens │ Rockwell │    │
│  │ (Snap7) │ (Pylogix)│    │
│  ├─────────┼──────────┤    │
│  │Mitsubish│   ABB    │    │
│  │(MCProto)│ (Modbus) │    │
│  ├─────────┼──────────┤    │
│  │  Fanuc  │  (more)  │    │
│  └─────────┴──────────┘    │
└─────────────────────────────┘
```

## ✨ Features

- 🔌 **Multi-PLC Support** — Siemens (S7), Rockwell (CIP), Mitsubishi (MC Protocol), ABB (Modbus/TCP), Fanuc
- 📖 **Read & Write** — Bool, Int, DInt, Real/Float, String data types
- 🩺 **Connection Diagnostics** — Health checks, connection pooling, timeout management
- 🖥️ **SCADA-Style UI** — Professional dark-themed dashboard with real-time feedback
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

## 📁 Project Structure

```
plc-diagnostics-bridge/
├── docker-compose.yml          # Orchestration
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
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

## 🛡️ Supported PLC Protocols

| Brand      | Protocol        | Library         | Data Types                    |
|------------|-----------------|-----------------|-------------------------------|
| Siemens    | S7 (ISO-on-TCP) | python-snap7    | Bool, Int, DInt, Real, String |
| Rockwell   | CIP / EtherNet/IP | pylogix       | Bool, Int, Float, String      |
| Mitsubishi | MC Protocol     | pymcprotocol    | Bool, Int, Float, String      |
| ABB        | Modbus/TCP      | pymodbus        | Bool, Int, Float, String      |
| Fanuc      | Custom          | —               | Read/Write                    |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is for internal diagnostic and testing purposes.

---

<p align="center">Built for industrial automation engineers 🏭</p>
