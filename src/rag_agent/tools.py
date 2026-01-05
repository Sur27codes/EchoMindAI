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
        search = DuckDuckGoSearchRun()
        return search.run(query)
    except Exception as e:
        return f"Error searching web: {str(e)}"

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

@tool
def generate_plot(code: str) -> str:
    """
    Useful for generating charts and graphs.
    Input should be Python code using matplotlib.pyplot as plt.
    
    IMPORTANT:
    - DO NOT save the file (plt.savefig). The tool handles this automatically.
    - DO NOT close the figure (plt.close). The tool needs the figure to remain open to save it.
    - Just create the plot (plt.plot, plt.title, etc).
    
    Example code:
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot([1, 2, 3], [1, 4, 9])
    plt.title('My Plot')
    """
    try:
        # Auto-inject the saving logic if missing? 
        # Better to just instruct the LLM to do it via prompt, but let's handle the filename for them to be safe.
        filename = f"chart_{int(time.time()*1000)}.png"
        filepath = chart_dir / filename
        
        # Prepend imports and append save logic if simple code provided
        full_code = f"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

{code}

# Ensure saved
if len(plt.get_fignums()) > 0:
    plt.savefig('{filepath}')
    plt.close()
"""
        repl = PythonREPL()
        output = repl.run(full_code)
        
        if filepath.exists():
            return f"Chart generated successfully: ![{filename}]({filepath})"
        else:
            return f"Executed code but no chart file was created. Output: {output}"
            
    except Exception as e:
        return f"Error generating plot: {str(e)}"
