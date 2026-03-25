FROM python:3.11-slim AS base

WORKDIR /app

# System deps (snap7 for Siemens)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libsnap7-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --compile -r requirements.txt

COPY . .

ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--log-level", "warning"]
