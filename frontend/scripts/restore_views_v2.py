"""
Extract view panels from original_index.html using line-based approach
and replace them in current index.html.
"""
import re

ORIGINAL = 'original_index.html'
CURRENT = 'index.html'

# Read both files as lines
with open(ORIGINAL, 'r', encoding='utf-8') as f:
    orig_lines = f.readlines()

with open(CURRENT, 'r', encoding='utf-8') as f:
    curr_lines = f.readlines()

# ── Helper: extract view panel content between two markers ──
def find_view_panel(lines, view_id):
    """Find a view panel by ID and return (start_line, end_line) or None."""
    target = f'id="{view_id}"'
    start = None
    for i, line in enumerate(lines):
        if target in line and 'class="view-panel"' in line:
            start = i
            break
    
    if start is None:
        return None
    
    # Now find the matching closing </section>
    # Count nesting of <section> tags
    stack = 0
    for i in range(start, len(lines)):
        line = lines[i]
        # Count opening <section (but not </section>)
        opens = len(re.findall(r'<section[>\s]', line))
        closes = line.count('</section>')
        stack += opens - closes
        if stack == 0:
            return (start, i)
    
    return None

# ── Extract all view panels from original ──
view_ids_original = []
for i, line in enumerate(orig_lines):
    m = re.search(r'id="(view-[^"]*)"', line)
    if m and 'class="view-panel"' in line:
        view_ids_original.append(m.group(1))

print("=== Original view panels ===")
original_panels = {}
for vid in view_ids_original:
    span = find_view_panel(orig_lines, vid)
    if span:
        content = ''.join(orig_lines[span[0]:span[1]+1])
        original_panels[vid] = content
        print(f"  {vid}: lines {span[0]+1}-{span[1]+1} ({len(content)} chars)")
    else:
        print(f"  {vid}: COULD NOT FIND")

# Extract all view panels from current
print("\n=== Current view panels ===")
current_panels = {}
view_ids_current = []
for i, line in enumerate(curr_lines):
    m = re.search(r'id="(view-[^"]*)"', line)
    if m and 'class="view-panel"' in line:
        view_ids_current.append(m.group(1))

for vid in view_ids_current:
    span = find_view_panel(curr_lines, vid)
    if span:
        content = ''.join(curr_lines[span[0]:span[1]+1])
        current_panels[vid] = (span[0], span[1], content)
        print(f"  {vid}: lines {span[0]+1}-{span[1]+1} ({len(content)} chars)")
    else:
        print(f"  {vid}: COULD NOT FIND")

# ── Replace simplified panels with original content ──
print("\n=== Replacing ===")
# Build new HTML content
current_text = ''.join(curr_lines)
new_additions = ['view-landing', 'view-auth-sign-in', 'view-admin-overview', 
                 'view-admin-clients', 'view-admin-settings', 
                 'view-expert-missions', 'view-expert-settings']

replacements = 0
for vid, orig_html in original_panels.items():
    if vid in new_additions:
        print(f"  ⏭️ {vid}: new addition, keeping current version")
        continue
    
    if vid in current_panels:
        _, _, curr_html = current_panels[vid]
        
        if curr_html != orig_html:
            if curr_html in current_text:
                current_text = current_text.replace(curr_html, orig_html, 1)
                replacements += 1
                print(f"  ✅ {vid}: {len(curr_html)} → {len(orig_html)} chars")
            else:
                print(f"  ❌ {vid}: current HTML not found in file")
        else:
            print(f"  ➡️ {vid}: already identical")
    else:
        print(f"  ❌ {vid}: not found in current")

print(f"\n✅ Replaced {replacements} view panels")

# ── Write back ──
with open(CURRENT, 'w', encoding='utf-8') as f:
    f.write(current_text)

print(f"✅ index.html written ({len(current_text)} chars)")
