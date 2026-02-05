

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from rag_agent.tools_external import get_images

def test_tool(query):
    print(f"\n--- Testing Tool: {query} ---")
    try:
        # get_images is a LangChain tool, invoke it
        res = get_images.invoke(query)
        print(f"Result: {res}")
        if "http" in res:
            print("✅ URL Found")
        else:
            print("❌ No URL")
    except Exception as e:
        print(f"❌ Error: {e}")

test_tool("tata motors")
test_tool("iphone 15 pro")

