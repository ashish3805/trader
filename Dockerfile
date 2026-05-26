# Python ADK Bridge Dockerfile
FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin-dir/
ENV PATH="/uv/bin-dir:${PATH}"

WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
COPY .env ./

# Install dependencies using uv
RUN uv sync --frozen --no-cache

# Copy source code
COPY . .

# Ensure mcp directory exists for the volume mount
RUN mkdir -p /app/mcp

# Default environment variables
ENV WA_BRIDGE_URL=http://whatsapp-provider:3000
ENV AGENT_MODEL=gemini-3.1-flash-lite

EXPOSE 6000

# We use uv run to ensure the virtualenv is active
CMD ["uv", "run", "python", "whatsapp_bridge.py"]
