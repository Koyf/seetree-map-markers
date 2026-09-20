FROM python:3.14-slim

# uv from its official image: reproducible install from uv.lock, no pip.
COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /bin/uv

WORKDIR /app

# Install deps first so this layer is cached while app code changes.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app ./app

EXPOSE 8000
CMD uv run --no-sync uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
