"""
Remove duplicated view-admin-clients panel and revert admin sidebar 
to point to shared clients view.
"""
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove the duplicated view-admin-clients section
# Find from the comment marker to the next view-panel
marker = '        <!-- ADMIN CLIENTS (separate copy) -->'
next_marker = '        <!-- EXPERT VIEWS -->'

if marker in content and next_marker in content:
    start = content.find(marker)
    end = content.find(next_marker, start)
    if end > start:
        content = content[:start] + content[end:]
        print(f"✅ Removed view-admin-clients duplication (removed {end-start} chars)")
    else:
        print("⚠️ Could not find end marker")
else:
    print(f"marker found: {marker in content}, next_marker: {next_marker in content}")
    # Try alternate approach
    if 'view-admin-clients' in content:
        idx = content.find('id="view-admin-clients"')
        # Find the section start and end
        # Start from the line containing the section
        lines = content[:idx].splitlines()
        section_start_line = len(lines) - 1  # approximate
        
        # Just remove the block by regex
        import re
        pattern = r'<!-- ADMIN CLIENTS \(separate copy\) -->.*?</section>\s*'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            content = content[:match.start()] + content[match.end():]
            print(f"✅ Removed view-admin-clients via regex")
        else:
            print("❌ Could not find via regex")

# 2. Revert admin sidebar to use shared clients view
old_admin_btn = 'data-view="admin-clients" style="display:none;">'
new_admin_btn = 'data-view="clients" style="display:none;">'
if old_admin_btn in content:
    content = content.replace(old_admin_btn, new_admin_btn, 1)
    print("✅ Reverted admin sidebar to shared clients view")
else:
    print("⚠️ Could not find admin-clients button to revert")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Done! File: {len(content)} chars")
