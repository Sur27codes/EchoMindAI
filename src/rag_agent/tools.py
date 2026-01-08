"""
Tools for the Multi-Modal RAG Agent.
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io
import time
from pathlib import Path
from datetime import datetime
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from langchain_community.tools import DuckDuckGoSearchRun
from deep_translator import GoogleTranslator

from .config import settings

# Initialize chart directory
chart_dir = settings.data_dir / "charts"
chart_dir.mkdir(parents=True, exist_ok=True)

@tool
def web_search(query: str) -> str:
    """
    Useful for searching the internet for improved accuracy, current events, or general knowledge.
    Returns snippets of web pages. 
    Use this to find LINKS and references for the user.
    """
    try:
        from .tools_external import _search_ddg
        # 1. Try robust browser-masqueraded search
        result = _search_ddg(query, f"Web Search Results for '{query}'")
        
        # 2. Wikipedia Fallback (if search fails or yields generic "no results")
        if "returned no results" in result or "Error" in result:
             try:
                 from langchain_community.tools import WikipediaQueryRun
                 from langchain_community.utilities import WikipediaAPIWrapper
                 wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
                 wiki_res = wiki.run(query)
                 if wiki_res and "No good Wikipedia Search" not in wiki_res:
                     return f"**Wikipedia Summary:**\n{wiki_res}\n\n(Note: Primary search failed, fell back to Wikipedia.)"
             except:
                 pass # Fallback failed too, return original error
                 
        return result
    except Exception as e:
        return f"Error searching web: {e}"

@tool
def calculator(expression: str) -> str:
    """
    Useful for performing mathematical calculations. 
    Input should be a valid Python mathematical expression (e.g., '123 * 456', 'sqrt(25)').
    """
    try:
        # Using a restricted eval for basic safety, though PythonREPL is also available
        # But this is faster for simple math
        allowed_names = {
            "sum": sum,
            "min": min,
            "max": max,
            "abs": abs,
            "round": round,
            "pow": pow,
            "len": len,
            "sorted": sorted,
        }
        # Safe math modules
        import math
        allowed_names.update({k: v for k, v in math.__dict__.items() if not k.startswith("__")})
        
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

import seaborn as sns

@tool
def generate_plot(code: str) -> str:
    """
    Useful for generating charts and graphs.
    Input should be Python code using matplotlib.pyplot as plt and seaborn as sns.
    ALWAYS save the figure to 'static/plot.png' and return the markdown link.
    """
    try:
        # Create static dir
        static_dir = Path("static")
        static_dir.mkdir(parents=True, exist_ok=True)
        
        # Enable Premium Visuals
        sns.set_theme(style="darkgrid", palette="rocket")
        
        # execution environment
        local_scope = {"plt": plt, "np": np, "pd": pd, "sns": sns}
        exec(code, {}, local_scope)
        
        # Save
        filename = f"plot_{int(time.time())}.png"
        save_path = static_dir / filename
        plt.savefig(str(save_path))
        plt.close()
        
        return f"![Chart](app/static/{filename})"
    except Exception as e:
        return f"Error generating plot: {e}"

@tool
def save_file(filename: str, content: str) -> str:
    """
    Saves text or code to a file. Use this to GENERATE reports, code, or documents.
    Args:
        filename: Name of the file (e.g. 'report.md', 'script.py').
        content: The full text content to write.
    """
    try:
        # Save to 'generated_outputs' to keep things organized
        out_dir = Path("data/generated_outputs")
        out_dir.mkdir(parents=True, exist_ok=True)
        file_path = out_dir / filename
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return f"✅ File successfully created at: `{file_path}`"
    except Exception as e:
        return f"Error saving file: {e}"

@tool
def translate_content(text: str, target_lang: str = "en") -> str:
    """
    Translate text to the target language (default 'en').
    Use this if the user speaks a different language or asks for translation.
    """
    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated
    except Exception as e:
        return f"Error translating: {e}"
