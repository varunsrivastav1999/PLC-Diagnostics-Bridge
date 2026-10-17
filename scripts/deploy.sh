#!/usr/bin/env bash
# ==============================================================================
# PLC Diagnostics Bridge - Automated Docker Deployment Script
# ==============================================================================
# Performs full zero-downtime/rebuild deployment:
# 1. Stops running containers
# 2. Pulls latest code from repository
# 3. Builds fresh Docker images
# 4. Starts all containers in daemon mode
# 5. Verifies health checks of Redis, Backend API, and Frontend
# ==============================================================================

set -eo pipefail

# ANSI color codes
C_RESET="\033[0m"
C_BOLD="\033[1m"
C_CYAN="\033[36m"
C_GREEN="\033[32m"
C_YELLOW="\033[33m"
C_RED="\033[31m"

log_info() {
    echo -e "${C_CYAN}${C_BOLD}[INFO]${C_RESET} $1"
}

log_success() {
    echo -e "${C_GREEN}${C_BOLD}[SUCCESS]${C_RESET} $1"
}

log_warn() {
    echo -e "${C_YELLOW}${C_BOLD}[WARN]${C_RESET} $1"
}

log_error() {
    echo -e "${C_RED}${C_BOLD}[ERROR]${C_RESET} $1" >&2
}

# Resolve repository root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
log_info "Working directory: $REPO_ROOT"

# Detect Docker Compose command (docker compose v2 vs docker-compose v1)
if docker compose version &>/dev/null; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &>/dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    log_error "Neither 'docker compose' nor 'docker-compose' was found on this system. Please install Docker Compose."
    exit 1
fi
log_info "Using Docker Compose binary: $DOCKER_COMPOSE"

# ------------------------------------------------------------------------------
# 1. Stop existing Docker containers
# ------------------------------------------------------------------------------
log_info "Step 1/5: Stopping existing Docker containers..."
if $DOCKER_COMPOSE ps -q | grep -q .; then
    $DOCKER_COMPOSE down --remove-orphans
    log_success "Existing containers stopped cleanly."
else
    log_info "No currently running containers detected. Continuing."
fi

# ------------------------------------------------------------------------------
# 2. Pull the latest code from the repository
# ------------------------------------------------------------------------------
log_info "Step 2/5: Pulling latest code from repository..."
if git rev-parse --is-inside-work-tree &>/dev/null; then
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    TARGET_BRANCH="${DEPLOY_BRANCH:-${CURRENT_BRANCH:-main}}"
    log_info "Fetching latest changes for branch: $TARGET_BRANCH"
    git fetch origin "$TARGET_BRANCH"
    git reset --hard "origin/$TARGET_BRANCH"
    log_success "Repository updated to commit: $(git rev-parse --short HEAD)"
else
    log_warn "Not a Git repository or .git folder not found. Skipping git pull."
fi

# ------------------------------------------------------------------------------
# 3. Build updated Docker images
# ------------------------------------------------------------------------------
log_info "Step 3/5: Building updated Docker images..."
$DOCKER_COMPOSE build --pull
log_success "Docker images built successfully."

# ------------------------------------------------------------------------------
# 4. Start containers
# ------------------------------------------------------------------------------
log_info "Step 4/5: Starting containers in detached mode..."
$DOCKER_COMPOSE up -d --remove-orphans
log_success "Containers started."

# ------------------------------------------------------------------------------
# 5. Verify all services are healthy and running
# ------------------------------------------------------------------------------
log_info "Step 5/5: Verifying health and connectivity of deployed services..."

MAX_RETRIES=20
RETRY_INTERVAL=3

# A. Verify Redis
log_info "Checking Redis health..."
REDIS_READY=false
for ((i=1; i<=MAX_RETRIES; i++)); do
    if $DOCKER_COMPOSE exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
        REDIS_READY=true
        log_success "Redis is UP and responding to PING."
        break
    fi
    echo -n "."
    sleep "$RETRY_INTERVAL"
done

if [ "$REDIS_READY" != "true" ]; then
    log_error "Redis failed health check after $((MAX_RETRIES * RETRY_INTERVAL))s."
    $DOCKER_COMPOSE logs redis --tail=30
    exit 1
fi

# B. Verify Backend API
log_info "Checking Backend API health (http://localhost:8000/health)..."
BACKEND_READY=false
for ((i=1; i<=MAX_RETRIES; i++)); do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        BACKEND_READY=true
        log_success "Backend API is UP and responding (HTTP 200 OK)."
        break
    fi
    echo -n "."
    sleep "$RETRY_INTERVAL"
done

if [ "$BACKEND_READY" != "true" ]; then
    log_error "Backend API failed health check (last HTTP code: $HTTP_CODE)."
    $DOCKER_COMPOSE logs backend --tail=50
    exit 1
fi

# C. Verify Frontend Web UI
log_info "Checking Frontend Web UI (http://localhost:8080/)..."
FRONTEND_READY=false
for ((i=1; i<=MAX_RETRIES; i++)); do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        FRONTEND_READY=true
        log_success "Frontend UI is UP and serving traffic (HTTP 200 OK)."
        break
    fi
    echo -n "."
    sleep "$RETRY_INTERVAL"
done

if [ "$FRONTEND_READY" != "true" ]; then
    log_error "Frontend Web UI failed health check (last HTTP code: $HTTP_CODE)."
    $DOCKER_COMPOSE logs frontend --tail=30
    exit 1
fi

echo ""
log_success "=================================================================="
log_success " PLC Diagnostics Bridge v3.0 Deployment Succeeded!"
log_success "=================================================================="
$DOCKER_COMPOSE ps
echo ""
log_info "Web UI:       http://localhost:8080"
log_info "Backend API:  http://localhost:8000"
log_info "API Docs:     http://localhost:8000/docs"
