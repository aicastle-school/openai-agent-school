#!/bin/bash
set -e

echo "🔧 Setting up development environment..."

# Install git-subtree
echo "📦 Installing git-subtree..."
wget -q https://raw.githubusercontent.com/git/git/master/contrib/subtree/git-subtree.sh -O /tmp/git-subtree.sh
chmod +x /tmp/git-subtree.sh
sudo mv /tmp/git-subtree.sh /usr/local/bin/git-subtree

# Install uv
echo "📦 Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
echo "📦 Syncing Python dependencies..."
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
