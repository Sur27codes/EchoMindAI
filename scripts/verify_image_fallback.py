
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from rag_agent.tools_external import get_images

def test_tool(query):
    print(f"\n--- Testing Tool: {query} ---")
    try:
        # get_images is a LangChain tool, invoke it
        res = get_images.invoke(query)
        print(f"Result Prefix: {res[:100]}...") # Print first 100 chars
        
        if "wikimedia" in res:
            print("✅ Wikimedia URL Found")
        elif "Generated Image" in res:
            print("✅ AI Generated Image Found")
        elif "http" in res and "duckduckgo" not in res and "google" not in res:
            print("✅ Direct Image URL Found")
        elif "Google Images" in res:
            print("❌ Failed - Returned Google Link (Should have used DALL-E?)")
        else:
            print("❓ Unknown Result Format")
            
    except Exception as e:
        print(f"❌ Error: {e}")

# Known to fail DDGS but succeed on Wiki
test_tool("Nike Logo")
test_tool("Tokyo Tower")

# Should use Hardcoded Map
test_tool("Tata Motors")
