#!/bin/bash
# Auto-sync activities to GitHub
# This script watches for changes to activities_database.json and auto-commits them

ACTIVITIES_FILE="docs/team_leads/activities_database.json"

# Check if file has changes
if git diff --quiet "$ACTIVITIES_FILE"; then
    echo "No changes to sync"
    exit 0
fi

# Commit and push changes
git add "$ACTIVITIES_FILE"
git commit -m "Auto-sync team activities - $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
git pull --rebase
git push

if [ $? -eq 0 ]; then
    echo "✓ Successfully synced activities to GitHub"
else
    echo "✗ Failed to sync activities"
    exit 1
fi
