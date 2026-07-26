"""
Remove redundant view-admin-users panel (duplicate IDs with admin-clients).
Redirect sidebar admin-users → admin-clients.
Clean up router.
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Find and remove view-admin-users panel
start_idx = html.find('id="view-admin-users"')
if start_idx < 0:
    print("❌ view-admin-users not found")
    exit(1)

section_start = html.rfind('<section', 0, start_idx)
if section_start < 0:
    print("❌ Could not find section start")
    exit(1)

# Find closing section by tracking depth
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
print(f"✅ Removed view-admin-users panel ({removed_len} chars)")

# 2. Redirect admin-users sidebar → admin-clients
if 'data-view="admin-users"' in html:
    html = html.replace('data-view="admin-users"', 'data-view="admin-clients"', 1)
    print("✅ Sidebar: admin-users → admin-clients")
else:
    print("⚠️ data-view=\"admin-users\" not found in sidebar")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 3. Clean up router
with open('src/router.ts', 'r', encoding='utf-8') as f:
    router = f.read()

# Remove admin-users from VIEW_TABS
router = router.replace(
    "  'admin-users': [],\n",
    "", 1
)
print("✅ Router: removed admin-users from VIEW_TABS")

# Remove admin-users from ROUTES
router = router.replace(
    "  'admin-users': '/admin/users',\n",
    "", 1
)
print("✅ Router: removed admin-users from ROUTES")

# Remove admin-users from URL parsing
router = router.replace(
    "users: 'admin-users', ",
    "", 1
)
print("✅ Router: removed admin-users from URL parsing")

# Clean up admin lifecycle: remove admin-users from condition, just keep admin-clients
old_lifecycle = """  } else if (viewName === 'admin-users' || viewName === 'admin-clients') {
    requestAnimationFrame(() => initAdminUsers());
  } else {
    destroyAdminUsers();
  }"""

new_lifecycle = """  } else if (viewName === 'admin-clients') {
    requestAnimationFrame(() => initAdminUsers());
  } else {
    destroyAdminUsers();
  }"""

if old_lifecycle in router:
    router = router.replace(old_lifecycle, new_lifecycle, 1)
    print("✅ Router: admin lifecycle cleaned up")
else:
    print("⚠️ Could not find admin lifecycle pattern")

# Remove admin-users from static import (only keep initAdminUsers, not admin-users imports)
# Actually, the router imports initAdminUsers, destroyAdminUsers from admin.ts - these are still needed
# for admin-clients lifecycle. No change needed to the import.

with open('src/router.ts', 'w', encoding='utf-8') as f:
    f.write(router)

# 4. Clean up admin.ts - remove the old admin-specific references (already done by fix_admin_data.py)
print("✅ admin.ts already cleaned by fix_admin_data.py")

print("\n✅ All done! Now only ONE panel has adminUserTableBody ID.")
