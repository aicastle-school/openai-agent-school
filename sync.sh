#!/bin/bash
set -e

echo "🔄 Starting update process..."

# Check if there are any changes
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ No changes to commit"
    exit 0
fi

# Show current changes
echo "📋 Changes to be committed:"
git status --short

# Add all changes
echo "📦 Adding all changes..."
git add -A

# Get commit message from argument or use default
COMMIT_MSG="${1:-Update: $(date +'%Y-%m-%d %H:%M:%S')}"

# Commit changes
echo "💾 Committing changes..."
git commit -m "$COMMIT_MSG"

# Pull with rebase to handle remote changes (local takes priority)
echo "📥 Pulling remote changes..."
if ! git pull --rebase origin main 2>/dev/null; then
    echo "⚠️  Conflict detected, resolving with local priority..."
    
    # Continue rebase, accepting local changes for conflicts
    git checkout --ours .
    git add -A
    git rebase --continue 2>/dev/null || echo "Rebase completed with conflicts resolved"
fi

# Push to remote
echo "📤 Pushing to remote..."
git push origin main

echo "✅ Update complete!"
echo ""
echo "📝 Committed: $COMMIT_MSG"
