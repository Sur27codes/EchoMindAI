
print("Verifying critical dependencies...")

try:
    import streamlit
    print("✅ streamlit imported")
except ImportError as e:
    print(f"❌ streamlit failed: {e}")

try:
    import duckduckgo_search
    print("✅ duckduckgo_search imported")
except ImportError as e:
    print(f"❌ duckduckgo_search failed: {e}")

try:
    import yfinance
    print("✅ yfinance imported")
except ImportError as e:
    print(f"❌ yfinance failed: {e}")

try:
    import wikipedia
    print("✅ wikipedia imported")
except ImportError as e:
    print(f"❌ wikipedia failed: {e}")

try:
    from deep_translator import GoogleTranslator
    print("✅ deep_translator imported")
except ImportError as e:
    print(f"❌ deep_translator failed: {e}")

try:
    import httpx
    print(f"✅ httpx imported (version: {httpx.__version__})")
except ImportError as e:
    print(f"❌ httpx failed: {e}")
    
print("Verification complete.")
