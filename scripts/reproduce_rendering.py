
import re
import sys

# Mocking the function from streamlit_app.py to test logic in isolation
def parse_mixed_content_original(text):
    """Original logic (simulated based on reading code)"""
    pattern = re.compile(
        r'(<section\s+class="weather-card">.*?</section>|<section\s+class="product-grid">.*?</section>|<div\s+class="product-card">.*?</div>|<div\s+class="financial-card".*?<!-- END_FINANCIAL_CARD -->)', 
        re.DOTALL | re.IGNORECASE
    )
    parts = []
    last_idx = 0
    for match in pattern.finditer(text):
        start, end = match.span()
        if start > last_idx:
            parts.append({"type": "text", "content": text[last_idx:start]})
        parts.append({"type": "html", "content": match.group(0)})
        last_idx = end
    if last_idx < len(text):
        parts.append({"type": "text", "content": text[last_idx:]})
    return parts

def parse_mixed_content_improved(text):
    """Proposed improved logic"""
    # 1. Un-indent HTML blocks that might be treated as code by Markdown
    # This regex looks for lines starting with 4 spaces that look like our widgets
    def unindent_block(match):
        block = match.group(0)
        return "\n".join([line.strip() for line in block.splitlines()])

    # Fix indentation for our specific widgets if they appear indented
    text = re.sub(r'((?:    )+<div class="financial-card".*?</div>)', unindent_block, text, flags=re.DOTALL)
    
    # 2. Relaxed Regex: Optional end comment, loose matching for closing tags
    # matches <div class="financial-card" ... > ... </div> (greedy until the matching close)
    # Note: Regex parsing HTML is fragile, but we target specific known widgets.
    
    patterns = [
        r'(<section\s+class="weather-card">.*?</section>)',
        r'(<section\s+class="product-grid">.*?</section>)',
        r'(<div\s+class="product-card">.*?</div>)',
        # We need to be careful with greedy matching if there are nested divs, but financial-card is usually flat-ish or controlled.
        # We'll rely on the specific class name.
        r'(<div\s+class="financial-card".*?</div>)' 
    ]
    
    combined_pattern = "|".join(patterns)
    pattern = re.compile(combined_pattern, re.DOTALL | re.IGNORECASE)
    
    parts = []
    last_idx = 0
    for match in pattern.finditer(text):
        start, end = match.span()
        if start > last_idx:
            parts.append({"type": "text", "content": text[last_idx:start]})
        parts.append({"type": "html", "content": match.group(0)})
        last_idx = end
    if last_idx < len(text):
        parts.append({"type": "text", "content": text[last_idx:]})
    return parts

# Test Cases
malformed_input = """Here is the data:

    <div class="financial-card" style="...">
        <div>AAPL</div>
        ...
    </div>
    
Hope that helps!"""

missing_comment_input = """Here is the data:
<div class="financial-card">
   Some data
</div>
Hope that helps!"""

def run_test():
    print("--- Testing Original Logic ---")
    res = parse_mixed_content_original(malformed_input)
    print(f"Indented Input detected {len([x for x in res if x['type']=='html'])} HTML blocks.")
    
    res2 = parse_mixed_content_original(missing_comment_input)
    print(f"Missing Comment Input detected {len([x for x in res2 if x['type']=='html'])} HTML blocks.")

    print("\n--- Testing Improved Logic ---")
    res3 = parse_mixed_content_improved(malformed_input)
    print(f"Indented Input detected {len([x for x in res3 if x['type']=='html'])} HTML blocks.")
    
    res4 = parse_mixed_content_improved(missing_comment_input)
    print(f"Missing Comment Input detected {len([x for x in res4 if x['type']=='html'])} HTML blocks.")

if __name__ == "__main__":
    run_test()
