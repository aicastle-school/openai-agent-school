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

# Setup Node.js environment
echo "📦 Setting up Node.js environment..."
if [ -d "${containerWorkspaceFolder}/chatkit" ]; then
    cd "${containerWorkspaceFolder}/chatkit"
    
    # Copy .env.local for chatkit app
    if [ -f .env.example ] && [ ! -f .env.local ]; then
        echo "📄 Creating .env.local for chatkit app..."
        cp .env.example .env.local
    fi
    
    # Install npm dependencies
    if [ -f package.json ]; then
        echo "Installing npm dependencies..."
        npm install
    fi
    
    cd "${containerWorkspaceFolder}"
fi

echo "✅ Development environment setup complete!"

