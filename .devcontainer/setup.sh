# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync Python dependencies
uv sync

# Copy environment example
cp .devcontainer/.env.example .env

