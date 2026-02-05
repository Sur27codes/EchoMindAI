
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    from rag_agent.tools_external import get_stock_price
    
    print("--- Testing 'tata stocks' ---")
    res = get_stock_price("tata stocks")
    
    if "financial-card" in res:
        print("✅ Financial Card Present")
    else:
        print("❌ Financial Card Missing")
        
    if "CHART_TOOL_JSON" in res:
        print("✅ Plotly Chart Payload Present")
        if "TATAMOTORS" in res or "TATASTEEL" in res:
             print("✅ Correct Ticker Resolved (Tata)")
    else:
        print("❌ Plotly Chart Payload Missing")
        
    print("\n--- Testing 'adani' ---")
    res2 = get_stock_price("adani")
    if "ADANIENT" in res2 or "ADANIGREEN" in res2:
        print("✅ Correct Ticker Resolved (Adani)")
        
except Exception as e:
    print(f"❌ Verification Failed: {e}")
