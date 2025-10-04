FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:$PATH"

RUN uv sync --frozen

CMD ["uv", "run", "mcp_server.py"]