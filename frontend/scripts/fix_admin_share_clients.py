"""
Point admin "Clients" and "Experts" tabs to the shared view-clients panel.
The assureur's view-clients is a rich panel with table, search, detail panel, and wizard.
This avoids duplicate ID issues and gives admin the exact same clients view.
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════════
# 1. Fix sidebar buttons: admin-clients → clients, admin-experts → clients
# ══════════════════════════════════════════════════════════════
html = html.replace(
    'data-view="admin-clients"',
    'data-view="clients"',
    1  # Only the first occurrence (the Clients button)
)
print("✅ Sidebar: admin Clients → clients (shared)")

html = html.replace(
    'data-view="admin-experts"',
    'data-view="clients"',
    1  # Only the first occurrence (the Experts button)
)
print("✅ Sidebar: admin Experts → clients (shared)")

# ══════════════════════════════════════════════════════════════
# 2. Remove view-admin-clients panel (including AdminClientsDetailPanel after it)
#    and view-admin-experts panel
# ══════════════════════════════════════════════════════════════

# Find and remove view-admin-experts first (it comes after admin-clients)
idx = html.find('id="view-admin-experts"')
if idx > 0:
    section_start = html.rfind('<section', 0, idx)
    after = html[section_start:]
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
    end_of_experts = section_start + i
    html = html[:section_start] + html[end_of_experts:]
    print(f"✅ Removed view-admin-experts panel")
else:
    print("⚠️ view-admin-experts not found")

# Find and remove view-admin-clients panel
idx = html.find('id="view-admin-clients"')
if idx > 0:
    section_start = html.rfind('<section', 0, idx)
    after = html[section_start:]
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
    end_of_clients = section_start + i

    # Check for AdminClientsDetailPanel dead code after the panel
    # This is the leftover detail panel content
    remaining = html[end_of_clients:]
    # Look for the next view-panel or </main>
    next_section = remaining.find('<section')
    next_main = remaining.find('</main>')
    if next_section > 0 and next_section < next_main:
        # There's something between admin-clients and the next section
        # Remove it up to the next section or </main>
        end_cleanup = next_section if next_section > 0 else next_main
        html = html[:section_start] + remaining[end_cleanup:]
        print(f"✅ Removed view-admin-clients panel + dead code after it")
    else:
        html = html[:section_start] + remaining
        print(f"✅ Removed view-admin-clients panel")
else:
    print("⚠️ view-admin-clients not found")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# ══════════════════════════════════════════════════════════════
# 3. Clean up router
# ══════════════════════════════════════════════════════════════
with open('src/router.ts', 'r', encoding='utf-8') as f:
    router = f.read()

# Remove admin-clients and admin-experts from VIEW_TABS
router = router.replace("  'admin-clients': [],\n", "", 1)
router = router.replace("  'admin-experts': [],\n", "", 1)
print("✅ VIEW_TABS: removed admin-clients and admin-experts")

# Remove from ROUTES
router = router.replace("  'admin-clients': '/admin/clients',\n", "", 1)
router = router.replace("  'admin-experts': '/admin/experts',\n", "", 1)
print("✅ ROUTES: removed admin-clients and admin-experts")

# Update URL parsing: redirect both to shared clients view
old_url = "const map: Record<string, string> = { overview: 'admin-overview', clients: 'admin-clients', experts: 'admin-experts', settings: 'settings' };"
new_url = "const map: Record<string, string> = { overview: 'admin-overview', clients: 'clients', experts: 'clients', settings: 'settings' };"
if old_url in router:
    router = router.replace(old_url, new_url, 1)
    print("✅ URL parsing: /admin/clients → clients (shared), /admin/experts → clients (shared)")
else:
    print("⚠️ Could not find URL parsing pattern")

# Update lifecycle: remove admin-clients and admin-experts
old_lifecycle = """  // Admin views lifecycle
  if (viewName === 'admin-overview') {
    import('./views/admin/admin.js').then(m => m.initAdminOverview ? m.initAdminOverview() : null);
  } else if (viewName === 'admin-clients') {
    requestAnimationFrame(() => initAdminUsers());
  } else if (viewName === 'admin-experts') {
    import('./views/admin/admin.js').then(m => m.initAdminExperts ? m.initAdminExperts() : null);
  } else {
    destroyAdminUsers();
    import('./views/admin/admin.js').then(m => { if (m.destroyAdminExperts) m.destroyAdminExperts(); });
  }"""

new_lifecycle = """  // Admin views lifecycle
  if (viewName === 'admin-overview') {
    import('./views/admin/admin.js').then(m => m.initAdminOverview ? m.initAdminOverview() : null);
  } else {
    // Only admin-overview admin-clients and admin-experts are now using the shared view
  }"""

if old_lifecycle in router:
    router = router.replace(old_lifecycle, new_lifecycle, 1)
    print("✅ Lifecycle: removed admin-clients and admin-experts lifecycle entries")
else:
    print("⚠️ Could not find admin lifecycle pattern, trying alternative...")
    # Try without the destroyAdminExperts
    alt_old = """  // Admin views lifecycle
  if (viewName === 'admin-overview') {
    import('./views/admin/admin.js').then(m => m.initAdminOverview ? m.initAdminOverview() : null);
  } else if (viewName === 'admin-clients') {
    requestAnimationFrame(() => initAdminUsers());
  } else if (viewName === 'admin-experts') {
    import('./views/admin/admin.js').then(m => m.initAdminExperts ? m.initAdminExperts() : null);
  } else {
    destroyAdminUsers();
  }"""
    if alt_old in router:
        router = router.replace(alt_old, new_lifecycle, 1)
        print("✅ Lifecycle: removed (alt match)")
    else:
        print("⚠️ Could not find lifecycle at all")

with open('src/router.ts', 'w', encoding='utf-8') as f:
    f.write(router)

print("\n✅ All done! Admin now uses shared view-clients for both Clients and Experts tabs.")
