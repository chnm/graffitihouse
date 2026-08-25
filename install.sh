#!/bin/bash

# ==========================================================================
# Setup script for installing project dependencies.
# NOTE: Run this script while in the project root directory.
# ==========================================================================

# Set script to exit on any errors.
set -e

# Test that uv is installed.
if ! command -v uv &> /dev/null
then
    echo "uv could not be found"
    echo "Please install uv before running this script"
    echo "https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Install project dependencies. uv creates and manages the .venv automatically.
echo "Installing dependencies with uv..."
uv sync
