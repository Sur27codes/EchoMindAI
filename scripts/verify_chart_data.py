
import yfinance as yf
import json
import pandas as pd

def get_stock_chart_payload(ticker):
    print(f"Fetching data for {ticker}...")
    stock = yf.Ticker(ticker)
    
    # Try fetching history
    try:
        # User wants "ups and downs", so 6mo or 1y is better than 1mo
        hist = stock.history(period="6mo")
        print(f"Rows fetched: {len(hist)}")
        
        if hist.empty:
            print("❌ History is empty.")
            return None
            
        # Transform for Plotly
        # We need a list of dicts: [{"Date": "...", "Close": 123}, ...]
        data = []
        for date, row in hist.iterrows():
            data.append({
                "Date": date.strftime("%Y-%m-%d"),
                "Close": round(row['Close'], 2)
            })
            
        payload = {
            "type": "line",
            "data": data,
            "x": "Date",
            "y": "Close",
            "title": f"Price History: {ticker} (6 Months)"
        }
        
        json_str = json.dumps(payload)
        return f"<!-- CHART_TOOL_JSON: {json_str} -->"
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# Test with a known ticker
res = get_stock_chart_payload("AAPL")
if res:
    print("\n✅ Payload Generated Successfully:")
    print(res[:100] + "...")
else:
    print("\n❌ Failed to generate payload.")
