
import re

def parse_mixed_content_check(text):
    # PRE-PROCESSING: Aggressive Strip
    if 'class="financial-card"' in text:
         text = re.sub(r'```(?:html|xml)?', '', text)
         text = text.replace('```', '')

    pattern = re.compile(
        r'(<section\s+class="weather-card">.*?</section>|<section\s+class="product-grid">.*?</section>|<div\s+class="product-card">.*?</div>|<div\s+class="financial-card".*?(?:<!-- END_FINANCIAL_CARD -->|</div>\s*</div>))', 
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

# Test Case: Tricky Layout
input_text = """Here is the data:
```html
Some intro text...
<div class="financial-card">
    Content
</div>
Some ending text...
```
End."""

print("--- Testing Loose Stripper ---")
res = parse_mixed_content_check(input_text)
html_blocks = [x for x in res if x['type'] == 'html']

print(f"Detected {len(html_blocks)} HTML blocks.")

if len(html_blocks) > 0:
    content = html_blocks[0]['content']
    print(f"Content: {content[:30]}...")
    if "```" not in content and "html" not in content[:10]:
         print("✅ Backticks stripped.")
    else:
         print("❌ Backticks present.")
