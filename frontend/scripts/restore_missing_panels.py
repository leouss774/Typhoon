"""
Restore missing view panels from git history.
Missing: view-overview, view-settings, view-assure-bien/travaux/engagement/dossier
"""
import subprocess
import re

# Get original HTML from git
result = subprocess.run(['git', 'show', 'HEAD:packages/front/index.html'], capture_output=True, text=True, cwd='..')
original = result.stdout
orig_lines = original.split('\n')

# Read current HTML
with open('index.html', 'r', encoding='utf-8') as f:
    current = f.read()
    curr_lines = current.split('\n')

def extract_panel(html_lines, panel_id):
    """Extract a view panel from the original HTML by its id."""
    full = '\n'.join(html_lines)
    idx = full.find(f'id="{panel_id}"')
    if idx < 0:
        print(f"❌ {panel_id} not found in original")
        return None
    
    # Find section start
    section_start = full.rfind('<section', 0, idx)
    if section_start < 0:
        print(f"❌ Could not find section start for {panel_id}")
        return None
    
    # Track nesting to find closing section
    after = full[section_start:]
    depth = 1
    i = after.find('>', 50) + 1
    while i < len(after) and depth > 0:
        next_open = after.find('<section', i)
        next_close = after.find('</section>', i)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            i = after.find('>', next_open) + 1
        else:
            depth -= 1
            i = next_close + 10
    
    panel_html = full[section_start:section_start + i]
    print(f"✅ Extracted {panel_id} ({len(panel_html)} chars)")
    return panel_html

def find_panel_line(html_lines, panel_id):
    """Find the line number where a panel starts."""
    for i, line in enumerate(html_lines):
        if f'id="{panel_id}"' in line and 'class="view-panel"' in line:
            return i
    return None

# Extract all missing panels
panels = {}
for pid in ['view-overview', 'view-settings', 'view-assure-bien', 'view-assure-travaux', 'view-assure-engagement', 'view-assure-dossier']:
    html = extract_panel(orig_lines, pid)
    if html:
        panels[pid] = html

# ── Insert panels into current HTML ──

# 1. Insert view-overview before view-portfolio (line 399 in current)
portfolio_line = find_panel_line(curr_lines, 'view-portfolio')
if portfolio_line and 'view-overview' in panels:
    # Find the exact position in the raw string
    target = '\n'.join(curr_lines[:portfolio_line])
    insert_pos = len(target) + 1  # +1 for the newline
    
    # Ensure we're not double-indenting
    overview_html = panels['view-overview']
    overview_html = '        ' + overview_html.lstrip()
    
    current = current[:insert_pos] + '\n' + overview_html + current[insert_pos:]
    print(f"✅ Inserted view-overview before view-portfolio")
    curr_lines = current.split('\n')

# 2. Insert view-settings after view-clients (before expert-missions)
# Find where expert-missions starts in the (possibly updated) current HTML
expert_line = find_panel_line(current.split('\n'), 'view-expert-missions')
if expert_line and 'view-settings' in panels:
    target = '\n'.join(current.split('\n')[:expert_line])
    insert_pos = len(target)
    
    settings_html = panels['view-settings']
    settings_html = '        ' + settings_html.lstrip()
    
    current = current[:insert_pos] + '\n' + settings_html + '\n        ' + current[insert_pos:]
    print(f"✅ Inserted view-settings before expert-missions")
    curr_lines = current.split('\n')

# 3. Insert view-assure-* panels after view-settings
# Find where view-expert-missions is (to insert before it)
# Actually insert them after view-settings, before expert-missions
# But since we inserted view-settings, we need to find the new positions

# Insert in order: view-assure-bien, view-assure-travaux, view-assure-engagement, view-assure-dossier
expert_missions_line = find_panel_line(current.split('\n'), 'view-expert-missions')
if expert_missions_line:
    # Insert before expert-missions
    for pid in ['view-assure-bien', 'view-assure-travaux', 'view-assure-engagement', 'view-assure-dossier']:
        if pid in panels:
            # Find current expert-missions position (it shifts after each insert)
            lines = current.split('\n')
            em_line = find_panel_line(lines, 'view-expert-missions')
            if em_line:
                target = '\n'.join(lines[:em_line])
                insert_pos = len(target)
                panel_html = panels[pid]
                panel_html = '        ' + panel_html.lstrip()
                current = current[:insert_pos] + '\n' + panel_html + current[insert_pos:]
                print(f"✅ Inserted {pid} before expert-missions")
            else:
                print(f"⚠️ Could not find expert-missions insertion point for {pid}")
else:
    print("⚠️ Could not find view-expert-missions insertion point")

# Write final HTML
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(current)

print("\n✅ All panels restored!")
