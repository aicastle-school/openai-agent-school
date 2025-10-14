#!/bin/bash
set -e

echo "🔧 Setting up development environment..."

# Install uv
echo "📦 Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync Python dependencies
echo "🐍 Syncing Python dependencies..."
uv sync

# Setup Python virtual environment activation
echo "🐍 Setting up Python virtual environment..."
echo 'source ${containerWorkspaceFolder}/.venv/bin/activate' >> ~/.bashrc

# Copy environment example
echo "📄 Copying .env.example..."
if [ -f .devcontainer/.env.example ]; then
    cp .devcontainer/.env.example .env
fi

echo "✅ Development environment setup complete!"

