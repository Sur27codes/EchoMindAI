
import re

def parse_mixed_content_check(text):
    # PRE-PROCESSING: Strip Markdown Code Blocks wrapping our widgets
    text = re.sub(r'```(?:html|xml)?\s*(<div class="financial-card".*?<!-- END_FINANCIAL_CARD -->)\s*```', r'\1', text, flags=re.DOTALL | re.IGNORECASE)

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

# Test Case: Wrapped in Code Block
input_text = """Here is the data:
```html
<div class="financial-card">
    Content
</div>
<!-- END_FINANCIAL_CARD -->
```
End."""

print("--- Testing Code Fence Strip ---")
res = parse_mixed_content_check(input_text)
html_blocks = [x for x in res if x['type'] == 'html']
print(f"Detected {len(html_blocks)} HTML blocks.")

if len(html_blocks) > 0:
    content = html_blocks[0]['content']
    print(f"Content Start: {content[:30]}...")
    if "```" not in content:
        print("✅ Code fences stripped.")
    else:
        print("❌ Code fences still present.")
else:
    print("❌ No HTML detected (Failed).")
