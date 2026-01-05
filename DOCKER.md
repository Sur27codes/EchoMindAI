# Docker Deployment Guide

## Quick Start

### Using Docker Compose (Recommended)

1. **Ensure your `.env` file is configured:**
   ```bash
   GROQ_API_KEY=gsk-your-actual-key
   RAG_CHAT_MODEL=openai/gpt-oss-20b
   # ... other settings
   ```

2. **Build and start:**
   ```bash
   docker-compose up --build
   ```

3. **Access the app:**
   Open `http://localhost:8501` in your browser

4. **Stop the container:**
   ```bash
   docker-compose down
   ```

### Using Docker directly

1. **Build the image:**
   ```bash
   docker build -t rag-agent .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name rag-agent \
     -p 8501:8501 \
     --env-file .env \
     -v $(pwd)/data:/app/data:ro \
     -v $(pwd)/artifacts/vectorstore:/app/artifacts/vectorstore \
     rag-agent
   ```

3. **View logs:**
   ```bash
   docker logs -f rag-agent
   ```

4. **Stop the container:**
   ```bash
   docker stop rag-agent
   docker rm rag-agent
   ```

## CLI Usage in Docker

For CLI operations (ingest, chat), use the CLI Dockerfile:

```bash
# Build CLI image
docker build -f Dockerfile.cli -t rag-agent-cli .

# Ingest documents
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  -v $(pwd)/artifacts/vectorstore:/app/artifacts/vectorstore \
  rag-agent-cli ingest

# Chat
docker run --rm -it \
  --env-file .env \
  -v $(pwd)/artifacts/vectorstore:/app/artifacts/vectorstore \
  rag-agent-cli chat "What is EchoMindAI?"
```

## Volume Mounts

- `./data:/app/data:ro` - Read-only mount for documents
- `./artifacts/vectorstore:/app/artifacts/vectorstore` - Persistent vector store

## Environment Variables

All environment variables from `.env` are passed to the container via `--env-file .env` or `docker-compose.yml`.

## Production Deployment

### Using Docker Compose

1. **Update `docker-compose.yml`** with production settings:
   ```yaml
   services:
     rag-agent:
       # ... existing config ...
       restart: always
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 4G
   ```

2. **Run in detached mode:**
   ```bash
   docker-compose up -d
   ```

### Using Docker Swarm or Kubernetes

The Dockerfile is compatible with orchestration platforms. You'll need to:
- Configure secrets management for API keys
- Set up persistent volumes for vectorstore
- Configure health checks
- Set resource limits

## Troubleshooting

### Container won't start
- Check logs: `docker-compose logs rag-agent`
- Verify `.env` file exists and has correct values
- Ensure ports 8501 is not in use

### Vector store not found
- Run ingestion first: `docker-compose run --rm rag-agent python -m rag_agent.cli ingest`
- Or mount existing vectorstore directory

### Out of memory
- Increase Docker memory limit
- Reduce `RAG_CHUNK_SIZE` in `.env`
- Use smaller embedding models

## Multi-stage Build Benefits

The Dockerfile uses multi-stage builds to:
- Reduce final image size
- Separate build dependencies from runtime
- Improve build caching

## Health Checks

The container includes a health check that verifies:
- Python environment is working
- Vector store directory exists
- Application can be imported

Check health status:
```bash
docker ps  # Look for "healthy" status
```

