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

# Setup Node.js workspace
echo "📦 Setting up Node.js workspace..."
if [ -f openai-chatkit-starter-app/package.json ]; then
    # Install dependencies using npm workspaces
    npm install
    
    # Remove root package-lock.json (not needed for workspaces)
    if [ -f package-lock.json ]; then
        echo "🗑️  Removing unnecessary root package-lock.json..."
        rm -f package-lock.json
    fi
    
    # Copy .env.local for chatkit app
    if [ -f openai-chatkit-starter-app/.env.example ] && [ ! -f openai-chatkit-starter-app/.env.local ]; then
        echo "📄 Creating .env.local for chatkit app..."
        cp openai-chatkit-starter-app/.env.example openai-chatkit-starter-app/.env.local
    fi
fi

# Make scripts executable
echo "🔧 Setting script permissions..."
if [ -f sync.sh ]; then
    chmod +x sync.sh
fi
if [ -f .devcontainer/pull_chatkit.sh ]; then
    chmod +x .devcontainer/pull_chatkit.sh
fi

echo "✅ Development environment setup complete!"
