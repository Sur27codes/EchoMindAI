
import re

def parse_mixed_content_check(text):
    # The updated regex in streamlit_app.py
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

# Test Case: Nested Divs
nested_input = """Here is the data:

<div class="financial-card">
    <div>
        Content inside nested div
    </div>
    <!-- Header -->
    More content
</div>
<!-- END_FINANCIAL_CARD -->

End of data."""

print("--- Testing Nested Div Logic ---")
res = parse_mixed_content_check(nested_input)

html_blocks = [x for x in res if x['type'] == 'html']
print(f"Detected {len(html_blocks)} HTML blocks.")

if len(html_blocks) > 0:
    content = html_blocks[0]['content']
    print(f"Block Content Length: {len(content)}")
    if "<!-- END_FINANCIAL_CARD -->" in content:
        print("✅ Correctly captured end tag.")
    else:
        print("❌ Failed to capture end tag (Truncated).")
        print("Captured:", content)
else:
    print("❌ No HTML detected.")
