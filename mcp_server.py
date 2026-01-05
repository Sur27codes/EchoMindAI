"""
MCP Server for EchoMindAI.
Exposes the RAG Agent capabilities as MCP tools.
"""
import asyncio
import sys
from pathlib import Path
import os
import warnings

# Suppress warnings
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
warnings.filterwarnings("ignore")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp.server.fastmcp import FastMCP
from rag_agent.rag_agent import RAGAgent
from rag_agent.ingest import ingest_documents as run_ingestion
from rag_agent.researcher import ResearchAgent
from rag_agent.config import settings

# Initialize FastMCP
mcp = FastMCP("EchoMindAI")

# Global agent instance (lazy loaded)
_agent = None

def get_agent():
    global _agent
    if _agent is None:
        try:
            print("Loading RAG Agent...", file=sys.stderr)
            _agent = RAGAgent()
        except Exception as e:
            print(f"Error loading agent: {e}", file=sys.stderr)
            return None
    return _agent

@mcp.tool()
async def ask_project_x(query: str) -> str:
    """
    Ask a question to the EchoMindAI RAG Agent.
    Use this tool when you need to retrieve information from the user's documents.
    
    Args:
        query: The question to ask.
    """
    agent = get_agent()
    if not agent:
        return "Error: RAG Agent could not be initialized. Please check the text embeddings and vector store."
    
    try:
        # We run the synchronous ask method in a thread to avoid blocking the async loop
        response = await asyncio.to_thread(agent.ask, query)
        return str(response)
    except Exception as e:
        return f"Error processing query: {str(e)}"

@mcp.tool()
async def ingest_knowledge_base() -> str:
    """
    Trigger the ingestion process to rebuild the vector knowledge base.
    Call this if the user adds new files or asks to refresh the data.
    """
    try:
        location = await asyncio.to_thread(run_ingestion)
        global _agent
        _agent = None  # Reset agent to force reload of new vector store
        return f"Successfully ingested documents. Vector store saved to {location}"
    except Exception as e:
        return f"Error during ingestion: {str(e)}"

# --- NEW TOOLS ---

@mcp.tool()
def calculator(expression: str) -> str:
    """
    Perform mathematical calculations.
    Example: "sqrt(144) * 2"
    """
    try:
        from rag_agent.tools import calculator as calc_tool
        return calc_tool.run(expression)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def web_search(query: str) -> str:
    """
    Search the internet for real-time information.
    """
    try:
        from rag_agent.tools import web_search as search_tool
        return search_tool.run(query)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def generate_plot(code: str) -> str:
    """
    Generate charts using matplotlib.
    Input: Python code using plt.
    Returns: Markdown link to the generated image.
    """
    try:
        from rag_agent.tools import generate_plot as plot_tool
        return plot_tool.run(code)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
async def deep_research(topic: str) -> str:
    """
    Perform a deep, multi-step research analysis on a topic.
    This tool plans, searches multiple sources, and writes a comprehensive report.
    Use this for complex questions that require more than a quick search.
    """
    try:
        # Helper to run synchronous generator
        def run_research():
            agent = ResearchAgent()
            gen = agent.execute_research(topic)
            last_val = ""
            for item in gen:
                if isinstance(item, str):
                    last_val = item
            return last_val
            
        return await asyncio.to_thread(run_research)
    except Exception as e:
        return f"Research failed: {e}"

@mcp.tool()
async def retrieve_documents(query: str) -> str:
    """
    Raw semantic search against the user's knowledge base.
    Returns the top 5 relevant document snippets.
    """
    agent = get_agent()
    if not agent:
        return "Agent not ready."
    
    docs = await asyncio.to_thread(agent.vector_store.similarity_search, query, k=5)
    return "\\n\\n---\\n\\n".join([f"Content: {d.page_content}" for d in docs])

@mcp.resource("echomindai://stats")
def get_stats() -> str:
    """Returns statistics about the current knowledge base."""
    stats = {
        "vector_dir": str(settings.vector_dir),
        "exists": settings.vector_dir.exists(),
        "data_dir": str(settings.data_dir),
        "embedding_model": settings.embedding_model
    }
    return str(stats)

if __name__ == "__main__":
    print("Starting EchoMindAI MCP Server...", file=sys.stderr)
    mcp.run()
