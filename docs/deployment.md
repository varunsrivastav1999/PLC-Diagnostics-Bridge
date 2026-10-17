# Docker Deployment & CI/CD Guide

This guide covers deploying **PLC Diagnostics Bridge v3.0** on a production server using Docker and the automated GitHub Actions CI/CD pipeline.

---

## 🚀 Quick Manual Deployment on Server

To deploy or update the application directly on the server, execute:

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### What `scripts/deploy.sh` Does:
1. **Stops Existing Containers**: Cleanly stops running Docker containers (`docker compose down --remove-orphans`).
2. **Pulls Latest Code**: Fetches and fast-forwards the latest code from `origin/main`.
3. **Builds Fresh Images**: Rebuilds frontend, backend, and redis containers (`docker compose build --pull`).
4. **Starts Containers**: Runs the full stack in background mode (`docker compose up -d`).
5. **Verifies Service Health**:
   - Pings Redis (`redis-cli ping -> PONG`)
   - Verifies Backend API (`http://localhost:8000/health -> HTTP 200`)
   - Verifies Frontend UI (`http://localhost:8080/ -> HTTP 200`)
   - Displays running container status table (`docker compose ps`)

---

## 🔄 Automated CI/CD Pipeline (GitHub Actions)

The pipeline defined in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) triggers on every push to `main` and on pull requests.

### Pipeline Stages:
1. **`backend-test`**: Runs Python 3.11 unit tests via `pytest` with cached pip dependencies.
2. **`frontend-build`**: Validates Node.js 20 build and compiles production assets with Vite.
3. **`docker-build`**: Validates that all Docker images build cleanly.
4. **`deploy`**: Connects to the server over SSH and executes `scripts/deploy.sh` to update and verify the running containers.

---

## 🔑 Configuring GitHub Secrets for Continuous Deployment

In your GitHub repository, navigate to **Settings** → **Secrets and variables** → **Actions** → **New repository secret**, and add:

| Secret Name | Description | Example |
|---|---|---|
| `SERVER_HOST` | Server IP or domain name | `192.169.4.100` or `plc.mycompany.com` |
| `SERVER_USER` | SSH username on the server | `ubuntu` or `deploy` |
| `SERVER_SSH_KEY` | Private SSH key (ed25519 or rsa) | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `SERVER_PORT` | *(Optional)* SSH Port | `22` (default) |
| `DEPLOY_PATH` | *(Optional)* Path to the cloned repository | `/opt/PLC-Diagnostics-Bridge` |

> **Note**: If `SERVER_HOST` is not yet configured, the CI pipeline completes all testing and building steps and logs an informational warning without failing.
