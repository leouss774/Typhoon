"""
Extract view-clients from both current and original HTML to compare.
"""
import re, os

# Find original file
original_path = None
candidates = [
    '/c/tmp/insurance_original/packages/front/index.html',
    'C:/tmp/insurance_original/packages/front/index.html',
    '/tmp/insurance_original/packages/front/index.html',
]
for p in candidates:
    if os.path.exists(p):
        original_path = p
        break

if not original_path:
    print("Original file not found!")
    exit(1)

print(f"Using original: {original_path}")

def extract_view(html_file, view_id):
    """Extract a view panel from HTML file."""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.splitlines()
    start = None
    target = 'id="' + view_id + '"'
    for i, line in enumerate(lines):
        if target in line and 'class="view-panel"' in line:
            start = i
            break
    
    if start is None:
        return None, None
    
    # Find end (next view-panel or file end)
    end = len(lines)
    for j in range(start+1, len(lines)):
        if 'class="view-panel"' in lines[j] and j > start + 1:
            # Count section nesting to find the right closing
            end = j
            break
    
    return start+1, '\n'.join(lines[start:end])

# Extract from current
current_line, current_html = extract_view('index.html', 'view-clients')
print(f"\n=== CURRENT view-clients (starts at line {current_line}) ===")
print(f"Length: {len(current_html)} chars")

# Check for detail panel elements
detail_ids = ['clientsDetailPanel', 'cdpBackBtn', 'cdpAvatar', 'cdpName', 'cdpEditToggle', 'cdpEvaluateBtn']
for did in detail_ids:
    if did in current_html:
        # Find the line
        for i, line in enumerate(current_html.splitlines()):
            if did in line:
                print(f"  ✅ {did} found at line {i+1}: {line.strip()[:80]}")
                break
    else:
        print(f"  ❌ {did} NOT found in current view-clients")

# Extract from original
orig_line, orig_html = extract_view(original_path, 'view-clients')
print(f"\n=== ORIGINAL view-clients (starts at line {orig_line}) ===")
print(f"Length: {len(orig_html)} chars")

for did in detail_ids:
    if did in orig_html:
        for i, line in enumerate(orig_html.splitlines()):
            if did in line:
                print(f"  ✅ {did} found at line {i+1}: {line.strip()[:80]}")
                break
    else:
        print(f"  ❌ {did} NOT found in original view-clients")
