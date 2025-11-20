#!/bin/bash
# Start the Activity Tracking API Server
# This server enables cross-user activity syncing

echo "Starting Activity Tracking API Server..."
echo "=========================================="

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ Flask not found. Installing dependencies..."
    pip3 install flask flask-cors
fi

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Start the API server
python3 activity_api.py
