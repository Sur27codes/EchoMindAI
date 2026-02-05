
import re

# This is the string visible in the user's screenshot
# It starts with text, then the div.
full_response = """Here is the current stock data for NVIDIA (Ticker: NVDA):

<div class="financial-card" style="font-family: sans-serif; padding: 20px; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(0,0,0,0.2)); width: 100%; max-width: 400px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">

    <!-- Header -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
        <div>
            <div style="font-size: 1.1rem; font-weight: bold; letter-spacing: 0.5px;">NVDA</div>
            <div style="font-size: 0.8rem; color: #aaa;">Real-Time Market Data</div>
        </div>
        <div style="font-size: 1.5rem;">📈</div>
    </div>

    <!-- Main Price -->
    <div style="margin-bottom: 20px;">
        <span style="font-size: 2.5rem; font-weight: 700; color: #fff;">$184.89</span>
        <div style="color: #4caf50; font-weight: 600; font-size: 1rem; margin-top: 5px;">
            +0.15 (+0.08%)
        </div>
    </div>
</div>
<!-- END_FINANCIAL_CARD -->
"""

print("--- Testing Current Regex ---")

# Current Regex in Streamlit App
pattern = re.compile(
    r'(<section\s+class="weather-card">.*?</section>|<section\s+class="product-grid">.*?</section>|<div\s+class="product-card">.*?</div>|<div\s+class="financial-card".*?<!-- END_FINANCIAL_CARD -->)', 
    re.DOTALL | re.IGNORECASE
)

for match in pattern.finditer(full_response):
    print("MATCH FOUND:")
    print(f"Start: {match.start()}, End: {match.end()}")
    content = match.group(0)
    print(f"Content Length: {len(content)}")
    if "<!-- END_FINANCIAL_CARD -->" in content:
        print("✅ End tag present")
    else:
        print("❌ End tag MISSING")
        print("Tail of content:", content[-50:])

# If no match
if not pattern.search(full_response):
    print("❌ NO MATCH FOUND AT ALL")
