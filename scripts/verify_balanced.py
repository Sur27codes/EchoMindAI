
# We will verify the logic by "mocking" the function since Streamlit context makes it hard to import directly
# But wait, parse_mixed_content is a pure helper, I can import it if I strip streamlit dependencies or just copy paste the logic to verify? 
# IMPORTING is risky if streamlit_app.py has top-level code that runs on import (like st.set_page_config).
# Checking file...
# It has `if __name__ == "__main__": main()`, but does it have top level calls?
# Yes: `st.set_page_config...` is usually at the top.
# So I will COPY the logic into the test script to ensure IT WORKS as written.

import re

def extract_balanced_tag(text, start_match, tag_name):
    """
    Extracts a balanced tag (div/section) starting from the regex match.
    start_match: the re.Match object for the opening tag WITHIN 'text'
    tag_name: "div" or "section"
    Returns: (content_string, end_index_absolute)
    """
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

def parse_mixed_content(text):
    """Splits text into text and HTML widget chunks using balanced parsing."""
    # PRE-PROCESSING: Global Stripper
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
        
        # Fix: Call extract on SUBTEXT
        w_content, w_end_rel = extract_balanced_tag(subtext, match, tag_type)
        
        if w_content:
            parts.append({"type": "html", "content": w_content})
            current_idx += w_end_rel
        else:
            parts.append({"type": "text", "content": subtext[:rel_start+1]})
            current_idx += rel_start + 1
            
    return parts

# Real User Failure Case (Nested Divs)
nested_html = """
Here is the data:
<div class="financial-card">
  <div class="header">
     <div class="title">Nested</div>
  </div> <!-- Double closing div -->
  <div class="body">Body</div>
</div>
End.
"""

print("--- Final Verification ---")
parts = parse_mixed_content(nested_html)
for p in parts:
    print(f"Type: {p['type']}")
    if p['type'] == 'html':
        print(f"Content: {p['content']}")
        if '<div class="body">' in p['content']:
            print("✅ SUCCESSS: Found body beyond nested divs.")
        else:
            print("❌ FAIL: Truncated early.")
