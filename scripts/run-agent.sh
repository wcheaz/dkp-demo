#!/bin/bash

# ============================================================================
# PydanticAI Agent Server Runner
# ============================================================================
# This script runs the agent server using uv (if available) or pip/venv.
# The agent listens on 0.0.0.0:8000.
#
# Adapt this script if your agent entry point differs (e.g., different module,
# different port). The entry point is defined in src/main.py which creates
# a FastAPI app with SSE transport.
#
# uv package manager detection:
# The script tries to find uv in standard locations (PATH, ~/.cargo/bin,
# VS Code snap). Install uv via 'pip install uv' or
# 'curl -LsSf https://astral.sh/uv/install.sh | sh' to use it.
# ============================================================================

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

# Run the agent using uv if found, otherwise fall back to pip
if [ -n "$UV_CMD" ]; then
    # Kill any process running on port 8000
    fuser -k 8000/tcp || true
    
    echo "Running agent using uv..."
    $UV_CMD run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "uv not found, falling back to pip..."
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "Error: Virtual environment not found."
        echo "RECOVERY STEPS:"
        echo "1. Run setup-agent.sh to create virtual environment"
        echo "2. Check if venv directory exists in current location"
        echo "3. Verify you're in the correct project directory"
        echo "4. Ensure you have Python installed"
        exit 1
    fi
    
    # Run the agent
    python src/main.py
fi
