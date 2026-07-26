"""
Replace simplified view panels in current index.html 
with the original rich content from the GitHub version (original_index.html).

Keeps new additions: admin views, expert views, landing page, auth view, Outfit font, tab handlers.
"""
import re

ORIGINAL_FILE = 'original_index.html'
CURRENT_FILE = 'index.html'

# ── 1. Read both files ────────────────────────────────────────
with open(ORIGINAL_FILE, 'r', encoding='utf-8') as f:
    original_html = f.read()

with open(CURRENT_FILE, 'r', encoding='utf-8') as f:
    current_html = f.read()

# ── 2. Extract original view panels ───────────────────────────
# Pattern to match <section class="view-panel" id="view-xxx"> ... </section>
# We need to capture the full section including nested <section> tags
def extract_view_panels(html):
    """Extract view panels using a stack-based approach for nested sections."""
    panels = {}
    pattern = re.compile(r'<section[^>]*class="view-panel"[^>]*id="(view-[^"]*)"[^>]*>')
    
    for match in pattern.finditer(html):
        view_id = match.group(1)
        start = match.start()
        
        # Parse the section with stack to handle nested <section> tags
        stack = 0
        i = start
        in_tag = False
        while i < len(html):
            if html[i] == '<':
                in_tag = True
                # Check for </section>
                if html[i:i+11] == '</section>':
                    stack -= 1
                    i += 10
                    if stack < 0:
                        # Found closing tag for our view panel
                        end = i + 1
                        panels[view_id] = html[start:end]
                        break
                # Check for <section (opening)
                elif html[i:i+9] == '<section' or html[i:i+8] == '<section':
                    # Make sure it's an opening tag, not a closing or self-closing
                    j = html.find('>', i)
                    if j > 0 and not html[i+1] == '/':
                        stack += 1
                        i = j
                    else:
                        i += 1
                else:
                    # Skip through the tag
                    j = html.find('>', i)
                    if j > 0:
                        i = j
                    else:
                        i += 1
            else:
                i += 1
        else:
            print(f"  ⚠️ Could not find closing tag for {view_id}")
    
    return panels

print("Extracting original view panels from GitHub version...")
original_panels = extract_view_panels(original_html)
print(f"  Found {len(original_panels)} panels in original")

print("\nExtracting current view panels...")
current_panels = extract_view_panels(current_html)
print(f"  Found {len(current_panels)} panels in current")

# ── 3. Replace simplified panels with original content ────────
print("\n=== Replacing view panels ===")
replacements_count = 0
skipped = 0
new_additions = ['view-landing', 'view-auth-sign-in', 'view-admin-overview', 
                 'view-admin-clients', 'view-admin-settings', 
                 'view-expert-missions', 'view-expert-settings']

for view_id in sorted(original_panels.keys()):
    if view_id in new_additions:
        skipped += 1
        continue
    
    if view_id in current_panels:
        old_html = current_panels[view_id]
        new_html = original_panels[view_id]
        
        old_len = len(old_html)
        new_len = len(new_html)
        
        if old_html != new_html:
            # Check if it appears in current_html
            if old_html in current_html:
                current_html = current_html.replace(old_html, new_html, 1)
                replacements_count += 1
                print(f"  ✅ {view_id}: {old_len} → {new_len} chars (+{new_len - old_len})")
            else:
                print(f"  ⚠️ {view_id}: exact match not found in current HTML!")
                # Try to find by id
                id_pattern = f'id="{view_id}"'
                if id_pattern in current_html:
                    print(f"     Found by id, but content differs too much for simple replace")
                    skipped += 1
                else:
                    print(f"     Could not find at all!")
        else:
            print(f"  ➡️ {view_id}: already identical, skipping")
    else:
        print(f"  ❌ {view_id}: not found in current HTML at all")
        skipped += 1

print(f"\n✅ Replaced {replacements_count} panels, skipped {skipped}")

# ── 4. Also extract and insert the settings sub-tab JS if present ──
# The original may have inline settings tab handling
# Check if original has a settings tab script we should preserve
settings_tab_pattern = r'<script>[\s\S]*?// Settings tabs[\s\S]*?</script>'
original_settings_script = re.search(settings_tab_pattern, original_html)
if original_settings_script:
    # Check if current already has it
    if original_settings_script.group(0) not in current_html:
        print("\nℹ️ Original settings tab script not found in current, extracting...")
        # Find insertion point - before the admin/expert tab handlers we added
        marker = '<!-- Inline tab handlers for admin/expert settings -->'
        if marker in current_html:
            current_html = current_html.replace(marker, 
                original_settings_script.group(0) + '\n\n    ' + marker)
            print("✅ Settings tab script added from original")

# ── 5. Write back ─────────────────────────────────────────────
with open(CURRENT_FILE, 'w', encoding='utf-8') as f:
    f.write(current_html)

print(f"\n✅ index.html updated with original view panels!")
print(f"   File size: {len(current_html)} chars")
