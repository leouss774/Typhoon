"""
Redirect admin-settings to the shared settings panel.
1. Change sidebar: admin-settings → settings
2. Fix URL parsing: admin/settings → settings (not admin-settings)
3. Remove view-admin-settings panel from HTML
4. Clean up router (remove admin-settings from VIEW_TABS, ROUTES)
"""
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove view-admin-settings panel
start_idx = html.find('id="view-admin-settings"')
if start_idx < 0:
    print("❌ view-admin-settings not found")
    exit(1)

# Find section start (go back to <section)
section_start = html.rfind('<section', 0, start_idx)
if section_start < 0:
    print("❌ Could not find section start")
    exit(1)

# Find the closing </section> by tracking depth
content = html[section_start:]
depth = 1
i = content.find('>', 50) + 1
while i < len(content) and depth > 0:
    next_open = content.find('<section', i)
    next_close = content.find('</section>', i)
    if next_close == -1:
        break
    if next_open != -1 and next_open < next_close:
        depth += 1
        i = content.find('>', next_open) + 1
    else:
        depth -= 1
        i = next_close + 10

section_end = section_start + i
removed_len = section_end - section_start
html = html[:section_start] + html[section_end:]
print(f"✅ Removed view-admin-settings panel ({removed_len} chars)")

# 2. Fix sidebar: admin-settings → settings
if 'data-view="admin-settings"' in html:
    html = html.replace('data-view="admin-settings"', 'data-view="settings"', 1)
    print("✅ Sidebar: admin-settings → settings")
else:
    print("⚠️ data-view=\"admin-settings\" not found in sidebar")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 3. Clean up router
with open('src/router.ts', 'r', encoding='utf-8') as f:
    router = f.read()

# Fix URL parsing: settings: 'admin-settings' → settings: 'settings'
old_url = "const map: Record<string, string> = { overview: 'admin-overview', clients: 'admin-clients', settings: 'admin-settings' };"
new_url = "const map: Record<string, string> = { overview: 'admin-overview', clients: 'admin-clients', settings: 'settings' };"
if old_url in router:
    router = router.replace(old_url, new_url, 1)
    print("✅ URL parsing: settings: 'admin-settings' → 'settings'")
else:
    print("⚠️ Could not find admin URL parsing pattern")

# Remove admin-settings from VIEW_TABS
router = router.replace("  'admin-settings': [],\n", "", 1)
print("✅ VIEW_TABS: removed admin-settings")

# Remove admin-settings from ROUTES
router = router.replace("  'admin-settings': '/admin/settings',\n", "", 1)
print("✅ ROUTES: removed admin-settings")

# Add settings lifecycle for admin (so initSettings is called)
# The current lifecycle only calls initSettings for 'settings', 'assureur-settings', 'assure-settings'
# We need to also call it when the user is in admin mode viewing settings
# Actually, since we're now redirecting admin/settings → settings (view='settings'),
# the existing lifecycle already handles it: `if (viewName === 'settings'...)` will match. ✅

# Check that the inline tab handlers in the script section reference admin-settings
# If so, we can remove them
if '#adminSettingsTabs' in router:
    # This is in the HTML file, not the router - already handled when we removed the panel
    pass

with open('src/router.ts', 'w', encoding='utf-8') as f:
    f.write(router)

# 4. Also remove the inline script for admin-settings tabs from the HTML
# The inline script references #adminSettingsTabs which no longer exists
# Let me clean that up too
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove admin settings tab handler from inline script
old_script = """      // Admin settings tabs
      document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('#adminSettingsTabs .settings-tab').forEach(function(tab) {
          tab.addEventListener('click', function() {
            document.querySelectorAll('#adminSettingsTabs .settings-tab').forEach(function(t) { t.classList.remove('active'); });
            this.classList.add('active');
            var target = this.getAttribute('data-stab');
            document.querySelectorAll('#view-admin-settings .settings-content').forEach(function(c) { c.classList.remove('active'); });
            var targetEl = document.querySelector('#view-admin-settings .settings-content[data-scontent="' + target + '"]');
            if (targetEl) targetEl.classList.add('active');
          });
        });
        // Expert settings tabs"""

new_script = """      // Expert settings tabs"""

if old_script in html:
    html = html.replace(old_script, new_script, 1)
    print("✅ Removed admin-settings inline tab handler")
else:
    print("⚠️ Could not find admin-settings inline tab handler")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("\n✅ Done! Admin now uses the shared rich settings panel.")
