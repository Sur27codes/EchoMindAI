#!/bin/bash
# Start the EchoMindAI MCP Server

# Ensure we are in the project root
cd "$(dirname "$0")"

# Check if mcp is installed
if ! pip show mcp > /dev/null 2>&1; then
    echo "Installing required dependencies..." >&2
    pip install -r requirements.txt
fi

# Run the server
python mcp_server.py
