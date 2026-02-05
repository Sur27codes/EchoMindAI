
import re

def parse_mixed_content(text):
    """Splits text into text and HTML widget chunks."""
    # Pattern for our specific widgets
    # Updated Robust Regex for <section> wrappers
    # Matches <section class="..."> with loose whitespace tolerance
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

def test_regex_nested():
    print("Testing Nested Div Regex...")
    sample_stock = """
Here is the stock:
```html
<div class="financial-card">
    <div class="header">
        Header Content
    </div>
    <div class="body">
        Body Content
    </div>
</div>
<!-- END_FINANCIAL_CARD -->
```
Ending text.
"""
    chunks = parse_mixed_content(sample_stock)
    print(f"Chunks found: {len(chunks)}")
    
    found_card = False
    for i, c in enumerate(chunks):
        content_preview = c['content'][:50].replace('\n', ' ')
        print(f"Chunk {i} ({c['type']}): {content_preview}...")
        
        if c['type'] == 'html' and '<div class="header">' in c['content']:
             found_card = True

    if found_card:
        print("✅ SUCCESS: Captured nested 'header' div inside financial card.")
    else:
        print("❌ FAILURE: Did not capture the full nested structure.")

if __name__ == "__main__":
    test_regex_nested()
