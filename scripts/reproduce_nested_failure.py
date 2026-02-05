
import re

def parse_mixed_content_check(text):
    # Current Regex (Double Div Terminator)
    pattern = re.compile(
        r'(<div\s+class="financial-card".*?(?:<!-- END_FINANCIAL_CARD -->|</div>\s*</div>))', 
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

# Test Case: Nested Divs ending together
# This is common in headers: <div> <div>Inner</div> </div>
nested_input = """
Start Text
<div class="financial-card">
    <div class="header">
        <div class="title">Stock Name</div>
    </div> <!-- This creates a </div></div> sequence! -->

    <div class="body">
        Price: $100
    </div>
</div>
End Text
"""

print("--- Testing Nested Div regex ---")
res = parse_mixed_content_check(nested_input)

html_blocks = [x for x in res if x['type'] == 'html']
print(f"Detected {len(html_blocks)} HTML blocks.")

if len(html_blocks) > 0:
    content = html_blocks[0]['content']
    print(f"Captured Content: \n{content}")
    
    if "Price: $100" in content:
        print("\n✅ Valid: Captured full card.")
    else:
        print("\n❌ Invalid: Truncated early (missing body).")
else:
    print("❌ No HTML detected.")
