#!/usr/bin/env bash

set -e  # stop on first error

# Move up to project root
cd "$(dirname "$0")/.."

# Set venv directory name
VENV_DIR=".venv"

# Create virtual environment if it does not exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
# For bash and zsh
source "$VENV_DIR/bin/activate"

# Upgrade pip within the venv
python -m pip install --upgrade pip

# Install dependencies if requirements.txt exists
if [ -f requirements.txt ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
elif [ -f pyproject.toml ]; then
    echo "Installing dependencies from pyproject.toml using pip..."
    pip install .
else
    echo "No requirements.txt or pyproject.toml found, skipping dependency installation."
fi
