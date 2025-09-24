#!/usr/bin/env bash

set -e  # stop on first error

# Move up to project root
cd "$(dirname "$0")/.."

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "uv not found, installing..."
    pip install uv
else
    echo "uv is already installed."
fi

# Sync dependencies
echo "Syncing dependencies..."
uv sync

# Pick script to run (default = scripts/myscript.py)
SCRIPT=${1:-scripts/myscript.py}

# Run the script
echo "Running $SCRIPT..."
uv run "$SCRIPT"
