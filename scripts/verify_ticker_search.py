
from duckduckgo_search import DDGS
import re

def lookup_ticker(query):
    print(f"Searching for: {query}")
    queries = [f"Yahoo Finance ticker {query}", f"find stock symbol for {query}", f"{query} share price"]
    
    clean_ticker = query
    found_ticker = None
    
    with DDGS() as ddgs:
        for i, q in enumerate(queries):
            print(f"  Query {i+1}: {q}")
            try:
                results = list(ddgs.text(q, max_results=3))
                if results:
                    # Combine text to search in
                    blob = " ".join([r['title'] + " " + r['body'] for r in results])
                    print(f"    Blob length: {len(blob)}")
                    
                    # Regex to find Ticker-like patterns:
                    # 1. Indian: WORD.NS or WORD.BO
                    indian_match = re.search(r'\b([A-Z0-9]{3,12}\.(?:NS|BO))\b', blob, re.IGNORECASE)
                    if indian_match:
                        found_ticker = indian_match.group(1).upper()
                        print(f"    ✅ MATCH (Indian): {found_ticker}")
                        break
                    
                    # 2. US: (AAPL) or "Symbol: AAPL"
                    us_match = re.search(r'(?:\(|Symbol:\s?|Code:\s?)([A-Z]{2,5})(?:\)| )', blob)
                    if us_match:
                        candidate = us_match.group(1).upper()
                        if candidate not in ["THE", "FOR", "AND", "STOCK", "INC", "LTD", "CORP"] and len(candidate) >= 2:
                            found_ticker = candidate
                            print(f"    ✅ MATCH (US): {found_ticker}")
                            break
            except Exception as e:
                print(f"    ❌ Query failed: {e}")
                
    if found_ticker:
        return found_ticker
    else:
        print("❌ No ticker found.")
        return None

print("--- Test Run ---")
lookup_ticker("tata stocks")
lookup_ticker("adani")
lookup_ticker("tesla")
