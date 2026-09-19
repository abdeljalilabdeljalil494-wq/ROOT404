# syntax=docker/dockerfile:1

##############################################################################
# Builder stage — install runtime dependencies into an isolated virtualenv.
##############################################################################
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

COPY requirements.txt ./
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

##############################################################################
# Final stage — production-only image.
#
# NOTE on ordering: the non-root `appuser` is created BEFORE the
# `COPY --chown=appuser:appuser` instruction. The original Dockerfile copied
# files with --chown before the user existed, which made the build fail.
##############################################################################
FROM python:3.12-slim

# Create the non-root user first so later --chown references resolve.
RUN groupadd --system --gid 1001 appuser \
    && useradd --system --uid 1001 --gid appuser --create-home \
               --shell /usr/sbin/nologin appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:${PATH}"

# Runtime dependencies only (compiled in the builder stage).
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY --chown=appuser:appuser app ./app

# Run as the non-root user (security hardening — keep).
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4).status == 200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
