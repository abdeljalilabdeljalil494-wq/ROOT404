FROM python:3.11-slim AS builder

WORKDIR /app

# Install build deps only in builder stage
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/home/appuser/.local/bin:$PATH

WORKDIR /app

# Install only runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    # Remove setuid binaries
    && find / -type f -perm -4000 -delete 2>/dev/null || true

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy app with correct permissions
COPY --chown=appuser:appuser app/ ./app/

# Create non-root user with no shell
RUN useradd -m -s /bin/false -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 750 /app && \
    mkdir -p /app/.cache && chown appuser:appuser /app/.cache && chmod 700 /app/.cache && \
    # Remove unnecessary files
    rm -rf /app/__pycache__ /app/*/__pycache__ 2>/dev/null || true

USER appuser

EXPOSE 8000

# Healthcheck with timeout
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Security: No new privileges, run with limited resources
# These are enforced via docker-compose security_opt and cap_drop

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--log-level", "info", "--access-log"]
