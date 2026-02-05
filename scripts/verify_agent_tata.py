
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from rag_agent.rag_agent import RAGAgent

print("--- Initializing Agent ---")
try:
    agent = RAGAgent()
    query = "dynamic graph of tata stocks"
    print(f"--- Asking: '{query}' ---")
    
    # We use the sync ask method for simplicity in debug
    response = agent.ask(query)
    
    print("\n--- Agent Response ---")
    print(response)
    
    if "financial-card" in response:
        print("\n✅ Financial Card Found in Response")
    else:
        print("\n❌ Financial Card MISSING")
        
    if "CHART_TOOL_JSON" in response:
        print("✅ Chart Payload Found")
    else:
        print("❌ Chart Payload MISSING")
        
except Exception as e:
    print(f"❌ Error running agent: {e}")
