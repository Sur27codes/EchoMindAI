
from src.rag_agent.tools_external import get_stock_price

print("--- Testing Stock Fallback ---")
print("Query: 'tata'")
res = get_stock_price("tata")
if "**Real-Time Search Results**" in res or "**Real-Time Search Results for 'tata' (Live Data Unavailable)**" in res:
    print("✅ Fallback Triggered Successfully!")
    print(res[:200] + "...")
else:
    print("❌ Fallback Failed or Unexpected Output:")
    print(res)
