#!/bin/bash

# Navigate to the agent directory
cd "$(dirname "$0")/../agent" || exit 1

# Try to find uv in various locations
UV_CMD=""
if command -v uv &> /dev/null; then
    UV_CMD="uv"
elif [ -f "$HOME/.cargo/bin/uv" ]; then
    UV_CMD="$HOME/.cargo/bin/uv"
elif [ -f "$HOME/snap/code/current/.local/bin/uv" ]; then
    UV_CMD="$HOME/snap/code/current/.local/bin/uv"
elif [ -f "$HOME/snap/code/217/.local/bin/uv" ]; then
    UV_CMD="$HOME/snap/code/217/.local/bin/uv"
fi

# Install dependencies using uv if found, otherwise fall back to pip
if [ -n "$UV_CMD" ]; then
    echo "Installing dependencies using uv..."
    $UV_CMD sync
else
    echo "uv not found, falling back to pip..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install -e .
fi
