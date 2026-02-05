
import re
import json

# --- MOCKED HELPERS FROM STREAMLIT_APP.PY ---

def extract_balanced_tag(text, start_match, tag_name):
    start_idx = start_match.start()
    balance = 0
    pattern = re.compile(f'(<{tag_name}\\b[^>]*>|</{tag_name}>)', re.IGNORECASE)
    
    for match in pattern.finditer(text, start_idx):
        tag = match.group(0).lower()
        if tag.startswith(f'<{tag_name}'):
            balance += 1
        else:
            balance -= 1
        
        if balance == 0:
            return text[start_idx:match.end()], match.end()
            
    return None, -1

def unindent_text(text):
    lines = text.splitlines()
    if not lines: return text
    min_indent = 1000
    for line in lines:
        if line.strip():
            indent = len(line) - len(line.lstrip())
            if indent < min_indent:
                min_indent = indent
    if min_indent == 1000 or min_indent == 0:
        return text
    return "\n".join([line[min_indent:] for line in lines])

def parse_mixed_content(text):
    if 'class="financial-card"' in text:
        text = text.replace("```html", "").replace("```xml", "").replace("```", "")
        
    parts = []
    current_idx = 0
    
    start_pattern = re.compile(
        r'(<section\s+class="weather-card">|<section\s+class="product-grid">|<div\s+class="product-card">|<div\s+class="financial-card")', 
        re.IGNORECASE
    )
    
    while current_idx < len(text):
        subtext = text[current_idx:]
        match = start_pattern.search(subtext)
        
        if not match:
            if subtext:
                parts.append({"type": "text", "content": subtext})
            break
            
        rel_start = match.start()
        abs_start = current_idx + rel_start
        
        if abs_start > current_idx:
            parts.append({"type": "text", "content": text[current_idx:abs_start]})
            
        tag_str = match.group(0).lower()
        tag_type = "section" if tag_str.startswith("<section") else "div"
        
        # FIX: Pass SUBTEXT to simulated behavior
        w_content, w_end_rel = extract_balanced_tag(subtext, match, tag_type)
        
        if w_content:
            parts.append({"type": "html", "content": w_content})
            current_idx += w_end_rel
        else:
            print("❌ extract_balanced_tag FAILED completely.")
            parts.append({"type": "text", "content": subtext[:rel_start+1]})
            current_idx += rel_start + 1
            
    return parts

# --- SIMULATED TOOL OUTPUT ---
stock_html = """
<div class="financial-card" style="...">
    <div style="display: flex;">
        <div>
            <div>ADANIGREEN.NS</div>
        </div>
    </div>
    <!-- Stats Grid -->
    <div style="display: grid;">
       <div>Item</div>
    </div>
</div>
<!-- END_FINANCIAL_CARD -->
<!-- CHART_DATA_JSON: [{"Date": "2023-01-01", "Close": 100}] -->
"""

input_clean = f"Here is the data:\n{stock_html}"

input_indented = f"""
Here is the data:

    {stock_html.replace(chr(10), chr(10) + '    ')}
"""

input_backticks = f"""
Here is the data:
```html
{stock_html}
```
"""

print("--- DEBUG RUN ---")

for name, inp in [("Clean", input_clean), ("Indented", input_indented), ("Backticks", input_backticks)]:
    print(f"\n[{name} Input Parsing]")
    parts = parse_mixed_content(inp)
    print(f"Chunks found: {len(parts)}")
    
    for i, p in enumerate(parts):
        print(f"  Chunk {i} Type: {p['type']}")
        if p['type'] == 'text':
            content = p['content']
            cleaned = unindent_text(content)
            
            # Check for JSON match
            json_match = re.search(r'<!-- CHART_DATA_JSON: (.*?) -->', cleaned)
            if json_match:
                print("    ✅ JSON Found in Text Chunk")
            
            if 'class="financial-card"' in cleaned:
                print("    ⚠️  WARNING: HTML found in TEXT chunk!")
                if "financial-card" in cleaned and ("class=" in cleaned or "class:" in cleaned):
                    print("    ✅ Safety Net would catch and force HTML.")
                else:
                    print("    ❌ Safety Net would FAIL.")
                    
        elif p['type'] == 'html':
             print("    ✅ HTML Chunk detected correctly.")
