
import yfinance as yf

tickers = ["TATAMOTORS.NS", "TATAMOTORS.BO", "TTM", "TATASTEEL.NS", "TCS.NS"]

print("--- Checking Tata Tickers ---")
for t in tickers:
    try:
        stock = yf.Ticker(t)
        # fast_info might trigger the fetch
        price = stock.fast_info.last_price
        print(f"✅ {t}: ${price}")
    except Exception as e:
        print(f"❌ {t}: Failed ({e})")
