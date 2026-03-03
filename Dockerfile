FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

# Install dependencies
RUN uv sync --no-dev

ENTRYPOINT ["uv", "run", "jfmo"]

# Default: daemon mode (used by docker compose with restart: unless-stopped)
# Override for one-shot: docker run ... jfmo run --apply
CMD ["daemon"]
