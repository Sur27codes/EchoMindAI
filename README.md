# EchoMindAI

This project demonstrates a lightweight Retrieval-Augmented Generation (RAG) agent powered by LangChain, Groq (for fast LLM inference), and a local FAISS vector store.

## Features
- Markdown/text ingestion from `data/docs`
- Chunking via `RecursiveCharacterTextSplitter`
- FAISS vector store persisted to `artifacts/vectorstore`
- Conversational agent that grounds ChatGPT-style responses on retrieved context

## Getting Started

### Option 1: Docker (Recommended)

1. **Build and run with Docker Compose**
   ```bash
   # Make sure your .env file is configured
   docker-compose up --build
   ```
   The app will be available at `http://localhost:8501`

2. **Or build and run manually**
   ```bash
   # Build the image
   docker build -t rag-agent .
   
   # Run the container
   docker run -p 8501:8501 \
     --env-file .env \
     -v $(pwd)/data:/app/data:ro \
     -v $(pwd)/artifacts/vectorstore:/app/artifacts/vectorstore \
     rag-agent
   ```

### Option 2: Local Development

1. **Install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   Create a `.env` file with your Groq API key:
   ```bash
   echo "GROQ_API_KEY=gsk-your-actual-groq-key-here" > .env
   ```
   
   **By default, the system uses Groq for LLM responses and OpenAI for embeddings.** 
   - The LLM (chat responses) uses: `openai/gpt-oss-20b` by default (via Groq)
   - The embeddings use: `text-embedding-3-small` by default (via OpenAI)
   - You can change the model by setting `RAG_CHAT_MODEL` or `RAG_EMBEDDING_MODEL` in `.env`
   
   **Available Groq models**: `openai/gpt-oss-20b`, `llama-3.1-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768`, `gemma-7b-it`
   
   **Groq parameters** (matching the example implementation):
   ```bash
   GROQ_TEMPERATURE=1.0          # Default: 1.0
   GROQ_MAX_TOKENS=8192          # Default: 8192
   GROQ_TOP_P=1.0                # Default: 1.0
   GROQ_REASONING_EFFORT=medium  # Default: medium (for models that support it)
   ```
   
   **For custom endpoints** (like local deployments), set `GROQ_BASE_URL` in your `.env` file:
   ```bash
   GROQ_BASE_URL=http://localhost:8000/v1
   ```
   
   **To use local embeddings**:
   - **Hugging Face embeddings**: Set `RAG_EMBEDDING_PROVIDER=huggingface`
   
   Optional overrides: `RAG_CHAT_PROVIDER`, `RAG_CHAT_MODEL`, `RAG_EMBEDDING_PROVIDER`, `RAG_EMBEDDING_MODEL`, `RAG_HF_EMBEDDING_MODEL`, `RAG_DATA_DIR`, `RAG_VECTOR_DIR`, `GROQ_BASE_URL`.

3. **Add documents**
   Drop `.md`/`.txt` files into `data/docs/`. A sample file is already included.

4. **Ingest**
   ```bash
   PYTHONPATH=src python -m rag_agent.cli ingest
   ```

   ```bash
   PYTHONPATH=src python -m rag_agent.cli chat "What guardrails do we enforce for incidents?"
   ```

5. **Run Streamlit Web UI** (recommended)
   
   **Option 1: Docker (easiest)**
   ```bash
   docker-compose up
   ```
   
   **Option 2: Use the startup script**
   ```bash
   ./start.sh
   ```
   This script will:
   - Create/activate the virtual environment automatically
   - Install/update all dependencies
   - Start the Streamlit app
   
   **Option 3: Manual start**
   ```bash
   source .venv/bin/activate
   streamlit run streamlit_app.py
   ```
   
   The web interface opens in your browser where you can:
   - Chat with the RAG agent interactively
   - View retrieved document sources
   - Upload new documents
   - Re-ingest documents with one click

6. **Programmatic sample**
   ```bash
   PYTHONPATH=src python examples/sample_run.py
   ```

## Project Layout
- `streamlit_app.py` – Streamlit web interface (recommended)
- `src/rag_agent/config.py` – central settings
- `src/rag_agent/ingest.py` – loaders, chunking, FAISS persistence
- `src/rag_agent/rag_agent.py` – conversational RAG chain
- `src/rag_agent/cli.py` – thin CLI for ingest/chat flows
- `src/rag_agent/embeddings.py` – embedding factory (OpenAI/Hugging Face)
- `src/rag_agent/llm.py` – LLM factory (Groq)

## Web Interface

The Streamlit app provides a user-friendly web interface with:
- 💬 Interactive chat interface with conversation history
- 📚 View retrieved document sources (optional debug mode)
- 📄 Upload and manage documents
- 🔄 One-click document re-ingestion
- ⚙️ Configuration display

Run with: `streamlit run streamlit_app.py`

## Docker Deployment

The project is fully containerized for easy deployment. See [DOCKER.md](DOCKER.md) for detailed instructions.

**Quick start with Docker:**
```bash
# Using Docker Compose (recommended)
docker-compose up --build

# Or using Docker directly
docker build -t rag-agent .
docker run -p 8501:8501 --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  -v $(pwd)/artifacts/vectorstore:/app/artifacts/vectorstore \
  rag-agent
```

The app will be available at `http://localhost:8501`

## Next Steps
- Add evaluation scripts (e.g., Ragas) to score grounded answers
- Add support for more document types (PDF, DOCX, etc.)
- Implement streaming responses for better UX

## Using Local Embeddings

To use local embeddings instead of OpenAI:

1. **Hugging Face embeddings**:
   - `RAG_EMBEDDING_PROVIDER=huggingface`
   - `RAG_HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2` (default, or any sentence-transformers model)
   - `HUGGINGFACEHUB_API_TOKEN=...` only if the model requires auth (most public models don't)

This setup uses local embeddings while still using Groq for fast LLM inference.



