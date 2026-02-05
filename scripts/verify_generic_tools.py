
import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from rag_agent.tools_external import get_global_news
from rag_agent.tools_visualization import create_chart

print("--- Testing Live Data (Global News) ---")
try:
    # "get_global_news" uses _fetch_news which uses ddgs.news
    res = get_global_news.invoke("artificial intelligence")
    print(f"Result Length: {len(res)}")
    if "No news found" in res or "Error" in res:
        print("❌ News Search Failed")
        print(res)
    else:
        print("✅ News Search Successful")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n--- Testing Generic Chart Tool ---")
try:
    # Simulate agent passing JSON for a bar chart
    # Scenario 1: Correct Usage (Data separately)
    # The tool expects 'data_json' to be just the data.
    # We invoke with a dictionary of arguments.
    print("Test 1: Correct Arguments")
    args = {
        "data_json": json.dumps({
            "cities": ["Tokyo", "Delhi", "Shanghai"],
            "population": [37, 29, 26]
        }),
        "chart_type": "bar",
        "x_col": "cities",
        "y_col": "population",
        "title": "City Population"
    }
    
    res = create_chart.invoke(args)
    print(f"Result: {res}")
    if "CHART_TOOL_JSON" in res:
        print("✅ Chart Payload Generated")
    else:
        print("❌ Chart Failed")
except Exception as e:
    print(f"❌ Error: {e}")
