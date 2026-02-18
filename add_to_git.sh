#!/bin/bash

# Check if a commit message was provided
if [ -z "$1" ]; then
    echo "Error: Commit message is required."
    echo "Usage: ./gitpush.sh \"Your commit message\""
    exit 1
fi

# Show current status
echo "📝 Git status before commit:"
git status

# Stage all changes
git add .

# Commit with the provided message
git commit -m "$1"

# Push to the default remote (usually origin)
echo "🚀 Pushing to GitHub..."
git push

# Show status after push
echo "✅ Done! Git status now:"
git status
