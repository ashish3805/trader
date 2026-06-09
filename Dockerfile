# --- Build Stage ---
FROM python:3.13-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin-dir/
ENV PATH="/uv/bin-dir:${PATH}"

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy only dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies into /app/.venv
# Using --no-install-project as we only want dependencies in this layer
RUN uv sync --frozen --no-cache --no-install-project --no-dev

# --- Runtime Stage ---
FROM python:3.13-slim

WORKDIR /app

# Copy the virtualenv from the builder stage
COPY --from=builder /app/.venv /app/.venv
# Ensure the virtualenv is used
ENV PATH="/app/.venv/bin:$PATH"

# Copy source code
COPY . .

# Ensure mcp directory exists
RUN mkdir -p /app/mcp

# Default environment variables
ENV WA_BRIDGE_URL=http://whatsapp-provider:3000
ENV AGENT_MODEL=gemini-3.1-flash-lite
ENV PYTHONUNBUFFERED=1

EXPOSE 6000

CMD ["python", "whatsapp_bridge.py"]
