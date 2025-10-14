#!/bin/bash
set -e

# Install git-subtree
wget -q https://raw.githubusercontent.com/git/git/master/contrib/subtree/git-subtree.sh -O /tmp/git-subtree.sh
chmod +x /tmp/git-subtree.sh
sudo mv /tmp/git-subtree.sh /usr/local/bin/git-subtree

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync Python dependencies
uv sync

# Copy environment example
cp .devcontainer/.env.example .env

# Setup Node.js environment
cd "${containerWorkspaceFolder}/chatkit"
cp .env.example .env.local
npm install
cd "${containerWorkspaceFolder}"

