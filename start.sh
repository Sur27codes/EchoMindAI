#!/bin/bash

# Script to start the RAG Agent Streamlit application
# This script activates the virtual environment and starts the app

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${GREEN}🚀 Starting RAG Agent Application...${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${GREEN}📦 Activating virtual environment...${NC}"
source .venv/bin/activate

# Check if we're in the venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip and critical dependencies
echo -e "${GREEN}⬆️  Upgrading pip...${NC}"
pip install --quiet --upgrade pip
pip install --quiet --upgrade duckduckgo-search

# Install/update dependencies
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}📚 Installing/updating dependencies...${NC}"
    pip install --quiet -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt not found${NC}"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating template...${NC}"
    # Use simple echo to avoid Heredoc EOF issues in editing
    echo "# API credentials" > .env
    echo "GROQ_API_KEY=gsk-your-groq-key" >> .env
    echo "RAG_CHAT_MODEL=openai/gpt-oss-20b" >> .env
    echo "GROQ_TEMPERATURE=1.0" >> .env
    echo "GROQ_MAX_TOKENS=8192" >> .env
    echo "GROQ_TOP_P=1.0" >> .env
    echo "GROQ_REASONING_EFFORT=medium" >> .env
    echo -e "${GREEN}✓ Template .env file created.${NC}"
fi

# Check if vector store exists
if [ ! -d "artifacts/vectorstore" ] || [ -z "$(ls -A artifacts/vectorstore 2>/dev/null)" ]; then
    echo -e "${YELLOW}⚠️  Vector store not found. You may need to ingest documents first.${NC}"
    echo -e "${YELLOW}   Run: PYTHONPATH=src python -m rag_agent.cli ingest${NC}"
fi

# Start Streamlit
echo -e "${GREEN}🌐 Starting Streamlit application...${NC}"
echo -e "${GREEN}   The app will open in your browser at http://localhost:8501${NC}"
echo ""
# Export PYTHONPATH and Suppress Warnings
export PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH}"
export TORCH_CPP_LOG_LEVEL=ERROR
export TRANSFORMERS_NO_ADVISORY_WARNINGS=1

## 5. Check and Clear Port 8501 (Streamlit Default)
echo "🔍 Checking port 8501..."
if lsof -i :8501 > /dev/null; then
    echo "⚠️  Port 8501 is busy. Killing zombie process..."
    lsof -ti :8501 | xargs kill -9
    sleep 2
    echo "✅ Port cleared."
fi

echo -e "${GREEN}🌐 Starting Streamlit application...${NC}"
echo -e "${GREEN}   The app will open in your browser at http://localhost:8501${NC}"
echo ""

streamlit run streamlit_app.py
