#!/bin/bash
# Quick test script for Docker setup

set -e

echo "🐳 Testing Docker Setup..."
echo "=========================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✓ Docker is installed"

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "⚠️  docker-compose not found, but you can still use 'docker build' and 'docker run'"
else
    echo "✓ docker-compose is available"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
GROQ_API_KEY=gsk-your-groq-key
RAG_CHAT_MODEL=openai/gpt-oss-20b
EOF
    echo "✓ Template .env created. Please update with your actual API key."
else
    echo "✓ .env file exists"
fi

# Check if data directory exists
if [ ! -d "data/docs" ]; then
    echo "⚠️  data/docs directory not found. Creating..."
    mkdir -p data/docs
    echo "✓ Created data/docs directory"
else
    echo "✓ data/docs directory exists"
fi

# Check if vectorstore directory exists
if [ ! -d "artifacts/vectorstore" ]; then
    echo "⚠️  artifacts/vectorstore directory not found. Creating..."
    mkdir -p artifacts/vectorstore
    echo "✓ Created artifacts/vectorstore directory"
else
    echo "✓ artifacts/vectorstore directory exists"
fi

echo ""
echo "=========================="
echo "✅ Docker setup check complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your GROQ_API_KEY"
echo "2. Add documents to data/docs/"
echo "3. Run: docker-compose up --build"
echo "   Or: docker build -t rag-agent . && docker run -p 8501:8501 --env-file .env rag-agent"

