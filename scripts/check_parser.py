
import re

def extract_balanced_div(text, start_pattern):
    """
    Finds a div starting with start_pattern and extracts it until the matching closing tag.
    Returns: (full_match_string, end_index) or (None, -1)
    """
    match = re.search(start_pattern, text, re.IGNORECASE)
    if not match:
        return None, -1

    start_idx = match.start()
    
    balance = 0
    # Scan all tags strictly
    tag_pattern = re.compile(r'(<div\b[^>]*>|</div>)', re.IGNORECASE)
    
    # Iterate from start_idx
    for tag_match in tag_pattern.finditer(text[start_idx:]):
        tag = tag_match.group(0).lower()
        if tag.startswith('<div'):
            balance += 1
        else:
            balance -= 1
        
        # When balance hits 0, we found the matching close!
        if balance == 0:
            # tag_match.end() is relative to text[start_idx:]
            end_abs = start_idx + tag_match.end()
            return text[start_idx:end_abs], end_abs
            
    return None, -1

def parse_mixed_content_balanced(text):
    # 1. Pre-process: Strip backticks if financial card exists
    if 'class="financial-card"' in text:
        text = text.replace("```html", "").replace("```xml", "").replace("```", "")

    parts = []
    current_idx = 0
    
    while current_idx < len(text):
        subtext = text[current_idx:]
        
        # Find next Start Tag
        match_start = re.search(r'<div\s+class="financial-card"', subtext, re.IGNORECASE)
        
        if not match_start:
            # No more cards, append rest as text
            if subtext:
                parts.append({"type": "text", "content": subtext})
            break
            
        rel_start = match_start.start()
        absolute_start = current_idx + rel_start
        
        # Add text before the card
        if absolute_start > current_idx:
            parts.append({"type": "text", "content": text[current_idx:absolute_start]})
            
        # Extract the balanced card
        # PASS SUBTEXT not FULL TEXT to ensure we find the one at this position
        card_content, end_abs = extract_balanced_div(text[absolute_start:], r'<div\s+class="financial-card"')
        
        if card_content:
            parts.append({"type": "html", "content": card_content})
            current_idx = absolute_start + len(card_content)
        else:
            # Logic error or malformed HTML?
            # If we matched the start regex but extract_balanced failed (e.g. no closing tag),
            # treating as text is safer.
            parts.append({"type": "text", "content": text[absolute_start:]})
            break
            
    return parts

# Test Cases
inputs = [
    # Case 1: Simple
    """Pre <div class="financial-card">Content</div> Post""",
    
    # Case 2: Nested Double Closing
    """Pre <div class="financial-card"> <div> <div>Inner</div> </div> </div> Post""",
    
    # Case 3: Wrapped in code blocks
    """Pre ```html <div class="financial-card"><div>Inner</div></div> ``` Post""",
    
    # Case 4: Multiple cards
    """Card1 <div class="financial-card">A</div> Card2 <div class="financial-card">B</div> End"""
]

print("--- Testing Balanced Parser ---")
for i, inp in enumerate(inputs):
    print(f"\nCase {i+1}:")
    parts = parse_mixed_content_balanced(inp)
    for p in parts:
        print(f"[{p['type'].upper()}]: {str(p['content']).strip()[:40]}...")
