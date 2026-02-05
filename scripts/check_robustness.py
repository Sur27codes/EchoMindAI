
import re

def parse_mixed_content_check(text):
    # PRE-PROCESSING: Strip Markdown Code Blocks wrapping our widgets
    text = re.sub(r'```(?:html|xml)?\s*(<div class="financial-card".*?(?:<!-- END_FINANCIAL_CARD -->|</div>\s*</div>))\s*```', r'\1', text, flags=re.DOTALL | re.IGNORECASE)

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

# Test Case 1: With Comment (Standard)
input_1 = """
<div class="financial-card">
  <div>Inner</div>
</div>
<!-- END_FINANCIAL_CARD -->
"""

# Test Case 2: Missing Comment (Problematic)
input_2 = """
<div class="financial-card">
  <div>Inner</div>
</div>
"""

# Test Case 3: Wrapped in Backticks + Missing Comment
input_3 = """
```html
<div class="financial-card">
  <div>Inner</div>
</div>
```
"""

print("--- Testing Robust Regex ---")
print("1. Standard:")
res1 = parse_mixed_content_check(input_1)
print(f"   Detected: {len([x for x in res1 if x['type'] == 'html'])}")

print("2. Missing Comment:")
res2 = parse_mixed_content_check(input_2)
print(f"   Detected: {len([x for x in res2 if x['type'] == 'html'])}")

print("3. Backticks + Missing:")
res3 = parse_mixed_content_check(input_3)
print(f"   Detected: {len([x for x in res3 if x['type'] == 'html'])}")

# Check content of 3
if len([x for x in res3 if x['type'] == 'html']) > 0:
    c = [x for x in res3 if x['type'] == 'html'][0]['content']
    if "```" not in c:
        print("   ✅ Backticks stripped.")
    else:
        print("   ❌ Backticks present.")
