# ---------------------------------------------------------
# Stage 1: Builder
# ---------------------------------------------------------
FROM python:3.12-slim AS builder

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Copy dependency definition files
COPY pyproject.toml README.md ./
COPY uv.lock ./

# Install dependencies via uv (without project package to cache dependencies)
RUN uv sync --frozen --no-install-project --no-dev

# Copy source code and build project
COPY src/ ./src/
RUN uv sync --frozen --no-dev

# ---------------------------------------------------------
# Stage 2: Runner
# ---------------------------------------------------------
FROM python:3.12-slim

# Prevent python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1
# Set path to the virtual environment created in builder
ENV PATH="/app/.venv/bin:$PATH"
# Explicitly set app env for production
ENV APP_ENV=production

WORKDIR /app

# Create a non-root user and group
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Create necessary directories and assign ownership
RUN mkdir -p /app/data && chown -R appuser:appgroup /app

# Copy the built virtual environment and application code from builder
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appgroup /app/src /app/src

# Switch to non-root user
USER appuser

# Expose the API port
EXPOSE 8000

# Healthcheck to verify the API is responsive
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

# Start the FastAPI application via uvicorn
CMD ["uvicorn", "src.presentation.api.app:create_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]
