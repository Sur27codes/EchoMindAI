"""
MCP Server for EchoMindAI.
Exposes the RAG Agent capabilities as MCP tools.
"""
import asyncio
import sys
from pathlib import Path
import os
import warnings
import logging

# Suppress noisy library warnings
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
warnings.filterwarnings("ignore", message=".*Examining the path of torch.classes.*")
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore") # Keep the general ignore as well

@mcp.tool()
def get_stock_price(ticker: str) -> str:
    """
    Get real-time stock price and percentage change for a company.
    """
    try:
        from rag_agent.tools_external import get_stock_price as stock_tool
        return stock_tool.run(ticker)
    except Exception as e:
        return f"Error: {e}"

# Configure logging
logging.basicConfig(level=logging.ERROR)

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

@mcp.tool()
def system_health() -> str:
    """
    Check the health of the RAG system, including vector store and API connectivity.
    """
    health_status = []
    
    # 1. Check Vector Store
    try:
        if settings.vector_dir.exists():
            health_status.append(f"✅ Vector Store: Found at {settings.vector_dir}")
        else:
            health_status.append(f"⚠️ Vector Store: Not found at {settings.vector_dir}")
    except Exception as e:
         health_status.append(f"❌ Vector Store Check Failed: {e}")

    # 2. Check Agent Loading
    try:
        agent = get_agent()
        if agent:
             health_status.append("✅ RAG Agent: Loaded successfully")
        else:
             health_status.append("❌ RAG Agent: Failed to load")
    except Exception as e:
        health_status.append(f"❌ RAG Agent Check Failed: {e}")
        
    return "\n".join(health_status)

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
def get_weather(city: str) -> str:
    """
    Get current weather and 7-day forecast for a city.
    """
    try:
        from rag_agent.tools_external import get_weather as w_tool
        return w_tool.run(city)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def get_historical_news(topic: str, time_range: str = 'd') -> str:
    """
    Get news from a specific time range: 'd' (day), 'w' (week), 'm' (month), 'y' (year).
    """
    try:
        from rag_agent.tools_external import _fetch_news_archive
        return _fetch_news_archive(topic, time_range)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def get_global_news(topic: str) -> str:
    """
    Get latest global news about a topic.
    """
    try:
        from rag_agent.tools_external import get_global_news as n_tool
        return n_tool.run(topic)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def find_hotels(query: str) -> str:
    """
    Find hotels, prices, and availability. 
    Example: "Hotels in Tokyo near Shinjuku"
    """
    try:
        from rag_agent.tools_external import find_hotels as h_tool
        return h_tool.run(query)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def search_products(item: str, location: str = None) -> str:
    """
    Find products, prices, and shopping links.
    Optional: Provide 'location' (e.g. "Austin TX") to find local stock/ratings.
    """
    try:
        from rag_agent.tools_external import search_products as s_tool
        return s_tool.run(item, location=location)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def find_flights(origin: str, destination: str, date: str = "soon") -> str:
    """
    Find flights, prices, and availability between cities.
    """
    try:
        from rag_agent.tools_external import find_flights as f_tool
        return f_tool.run(origin, destination, date)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def get_map_location(place: str) -> str:
    """
    Get map coordinates and links for a place.
    """
    try:
        from rag_agent.tools_external import get_map_location as m_tool
        return m_tool.run(place)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def get_images(query: str) -> str:
    """
    Find image URLs for a topic.
    """
    try:
        from rag_agent.tools_external import get_images as i_tool
        return i_tool.run(query)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def find_relevant_links(query: str) -> str:
    """
    Find official web links and resources.
    """
    try:
        from rag_agent.tools_external import find_relevant_links as l_tool
        return l_tool.run(query)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def generate_plot(code: str) -> str:
    """
    Generate charts using matplotlib/seaborn.
    Input: Python code using plt/sns.
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
async def retrieve_documents(query: str, k: int = 5) -> str:
    """
    Raw semantic search against the user's knowledge base.
    Returns the relevant document snippets.
    
    Args:
        query: The search query.
        k: Number of documents to retrieve (default 5).
    """
    agent = get_agent()
    if not agent:
        return "Agent not ready."
    
    try:
        # Limit k to reasonable bounds
        k = max(1, min(k, 20))
        docs = await asyncio.to_thread(agent.vector_store.similarity_search, query, k=k)
        
        if not docs:
            return "No matching documents found."
            
        return "\\n\\n---\\n\\n".join([f"Source: {d.metadata.get('source', 'Unknown')}\\nContent: {d.page_content}" for d in docs])
    except Exception as e:
        return f"Error retrieving documents: {str(e)}"

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

@mcp.tool()
def translate_content(text: str, target_lang: str = "en") -> str:
    """
    Translate text to a target language.
    target_lang: 'es' (Spanish), 'fr' (French), 'de' (German), etc.
    """
    try:
        from rag_agent.tools import translate_content as t_tool
        return t_tool.run(text, target_lang=target_lang)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def save_file(filename: str, content: str) -> str:
    """Save text or code to a file."""
    try:
        from rag_agent.tools import save_file as s_tool
        return s_tool.run(filename, content)
    except Exception as e:
        return f"Error saving file: {e}"

@mcp.tool()
def generate_ai_image(description: str) -> str:
    """Generate an image using AI (DALL-E 3)."""
    try:
        from rag_agent.tools_external import generate_ai_image as g_tool
        return g_tool.run(description)
    except Exception as e:
        return f"Error generating image: {e}"

@mcp.tool()
def get_images(query: str) -> str:
    """Find real images (Wikimedia/Google) or generate distinct visuals."""
    try:
        from rag_agent.tools_external import get_images as img_tool
        return img_tool.run(query)
    except Exception as e:
        return f"Error finding images: {e}"

@mcp.tool()
def find_relevant_links(query: str) -> str:
    """Find relevant web links, social media profiles, and official sites."""
    try:
        from rag_agent.tools_external import find_relevant_links as link_tool
        return link_tool.run(query)
    except Exception as e:
        return f"Error finding links: {e}"

@mcp.tool()
def find_hotels(query: str) -> str:
    """Find hotels, availability, and rates."""
    try:
        from rag_agent.tools_external import find_hotels as hotel_tool
        return hotel_tool.run(query)
    except Exception as e:
        return f"Error finding hotels: {e}"

@mcp.tool()
def find_flights(origin: str, destination: str, date: str = "soon") -> str:
    """Find flights and prices."""
    try:
        from rag_agent.tools_external import find_flights as flight_tool
        return flight_tool.run(origin, destination, date)
    except Exception as e:
        return f"Error finding flights: {e}"

@mcp.tool()
def analyze_image(image_path: str) -> str:
    """Analyze an image file and return a description."""
    try:
        from rag_agent.tools_vision import describe_image
        return describe_image(image_path)
    except Exception as e:
        return f"Error analyzing image: {e}"

@mcp.resource("echomindai://config")
def get_config() -> str:
    """Returns the current configuration settings."""
    import json
    # Create a safe subset of settings to expose
    config = {
        "chat_model": settings.chat_model,
        "chat_provider": settings.chat_provider,
        "embedding_model": settings.embedding_model,
        "data_dir": str(settings.data_dir),
        "vector_dir": str(settings.vector_dir),
        # Avoid exposing API keys directly if possible, or mask them
        "groq_api_key_set": bool(settings.groq_api_key),
    }
    return json.dumps(config, indent=2)

# --- PROMPTS ---

@mcp.prompt()
def explain_project() -> str:
    """
    Returns a prompt to explain the current project context or architecture.
    """
    return """
    You are a Senior Software Architect. Please analyze the codebase and provide a Master-Class explanation.
    
    Structure your response as follows:
    1.  **Architecture Diagram** (Mermaid): Visual overview.
    2.  **Core Components**: Deep dive into the `rag_agent`, `tools`, and `streamlit_app`.
    3.  **Data Flow**: How a user query transforms into an answer (Step-by-Step).
    4.  **Key Libraries**: Why we use `langchain`, `faiss`, `streamlit`, and `seaborn`.
    """

@mcp.prompt()
def debug_error(error_message: str) -> str:
    """
    Returns a prompt to help debug a specific error message.
    """
    return f"""
    You are an Expert Python Debugger. I have an error:
    
    ```
    {error_message}
    ```
    
    Please solve this using the "5 Whys" method:
    1.  **Root Cause Analysis**: What exactly failed?
    2.  **Code Inspection**: Which file/line is the culprit?
    3.  **Fix Strategy**: Step-by-step solution.
    4.  **Verification**: How to test the fix.
    
    Be precise. Do not guess.
    """

@mcp.prompt()
def generate_readme() -> str:
    """
    Returns a prompt to generate a README.md file for the project.
    """
    return """
    Generate a **World-Class README.md** for this project.
    
    It must include:
    -   **Badges**: Build status, version, license.
    -   **Hero Image**: (Placeholder).
    -   **Features Grid**: 3x3 table of capabilities (RAG, Vision, Voice, etc.).
    -   **Quick Start**: One-liner install commands.
    -   **Configuration**: How to set `.env`.
    -   **Architecture**: Brief explanation of the "EchoMindAI" brain.
    """

@mcp.prompt()
def daily_briefing(user_location: str = "London") -> str:
    """
    Returns a prompt to generate a comprehensive daily briefing.
    Args:
        user_location: The user's city for weather/local news.
    """
    return f"""
    Act as my **Chief of Staff**. Prepare a "Morning Intelligence Briefing".
    
    **Required Sections:**
    1.  **🌍 Global Situation Room**: Top 3 geopolitical or tech headlines. (Use `get_global_news`)
    2.  **🌦️ Local Intel ({user_location})**: Weather forecast & local events. (Use `get_weather`)
    3.  **💰 Market Watch**: S&P 500, NASDAQ, and Crypto trends. (Use `get_global_news`)
    4.  **📅 Daily Wisdom**: A relevant quote or productivity tip.
    
    Tone: Professional, Concise, Executive.
    """

@mcp.prompt()
def shopping_assistant(product_query: str) -> str:
    """
    Returns a prompt to help the user shop for a product.
    """
    return f"""
    You are a **Personal Shopping Concierge**. I want to buy: "{product_query}".
    
    **Execute this Plan:**
    1.  **Market Scan**: Find the current price range. (Use `search_products`)
    2.  **Visuals**: Find 3 clear images of the product. (Use `get_images`)
    3.  **Analysis**: List Pros/Cons based on reviews.
    4.  **Recommendation**: The best place to buy it right now (Amazon/BestBuy/etc).
    
    Output Format:
    -   **Product Name** (Price Range)
    -   [Image Carousel]
    -   **The Good**: ...
    -   **The Bad**: ...
    -   **Buy Here**: [Link]
    """

if __name__ == "__main__":
    import threading
    # Warmup Agent in background
    def warmup():
        print("Warming up RAG Agent...", file=sys.stderr)
        get_agent()
        print("RAG Agent Ready!", file=sys.stderr)
    
    threading.Thread(target=warmup, daemon=True).start()
    
    print("Starting EchoMindAI MCP Server...", file=sys.stderr)
    mcp.run()
