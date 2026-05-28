FROM python:3.11-slim AS base

WORKDIR /app

# System deps (snap7 for Siemens, plus diagnostics)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libsnap7-dev \
    curl iputils-ping tzdata \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --compile -r requirements.txt

COPY . .

ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Single worker — Redis handles cross-process I/O serialization
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "warning"]
