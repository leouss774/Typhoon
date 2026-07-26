"""
Fix: Keep admin role when clicking Clients/Experts tabs.
- Revert sidebar to admin-clients and admin-experts
- Keep VIEW_TABS, ROUTES, URL parsing for these
- Use panelViewName to map to shared 'clients' panel
- Add lifecycle for initClients
"""
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Revert sidebar: 'clients' → 'admin-clients' (but only the ADMIN buttons!)
# The admin sidebar buttons currently have data-view="clients" (both Clients and Experts)
# We need to find the admin-specific buttons and change them back

# Find the admin section in sidebar and fix
# Change the admin Clients button (groups icon) back to admin-clients
html = html.replace(
    'class="nav-item nav-role-admin" data-view="clients" style="display:none;"><span class="material-symbols-outlined">groups</span><span class="nav-label">Clients</span>',
    'class="nav-item nav-role-admin" data-view="admin-clients" style="display:none;"><span class="material-symbols-outlined">groups</span><span class="nav-label">Clients</span>',
    1
)
print("✅ Sidebar: admin Clients → admin-clients")

# Change the admin Experts button (verified icon) back to admin-experts
html = html.replace(
    'class="nav-item nav-role-admin" data-view="clients" style="display:none;"><span class="material-symbols-outlined">verified</span><span class="nav-label">Experts</span>',
    'class="nav-item nav-role-admin" data-view="admin-experts" style="display:none;"><span class="material-symbols-outlined">verified</span><span class="nav-label">Experts</span>',
    1
)
print("✅ Sidebar: admin Experts → admin-experts")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Fix router
with open('src/router.ts', 'r', encoding='utf-8') as f:
    router = f.read()

# 1. Add admin-clients and admin-experts back to VIEW_TABS
router = router.replace(
    "  'admin-overview': [],",
    "  'admin-overview': [],\n  'admin-clients': [],\n  'admin-experts': [],",
    1
)
print("✅ VIEW_TABS: restored admin-clients and admin-experts")

# 2. Add admin-clients and admin-experts back to ROUTES
router = router.replace(
    "  'admin-overview': '/admin/overview',",
    "  'admin-overview': '/admin/overview',\n  'admin-clients': '/admin/clients',\n  'admin-experts': '/admin/experts',",
    1
)
print("✅ ROUTES: restored admin-clients and admin-experts")

# 3. Fix URL parsing: keep admin-specific view names
old_url = "const map: Record<string, string> = { overview: 'admin-overview', clients: 'clients', experts: 'clients', settings: 'settings' };"
new_url = "const map: Record<string, string> = { overview: 'admin-overview', clients: 'admin-clients', experts: 'admin-experts', settings: 'settings' };"
if old_url in router:
    router = router.replace(old_url, new_url, 1)
    print("✅ URL parsing: fixed admin-clients and admin-experts")
else:
    print("⚠️ Could not find URL parsing pattern")

# 4. Add panelViewName mapping
old_panel = "const panelViewName = viewName === 'assureur-settings' || viewName === 'assure-settings' ? 'settings'\n    : viewName;"
new_panel = "const panelViewName = viewName === 'assureur-settings' || viewName === 'assure-settings' ? 'settings'\n    : viewName === 'admin-clients' || viewName === 'admin-experts' ? 'clients'\n    : viewName;"
if old_panel in router:
    router = router.replace(old_panel, new_panel, 1)
    print("✅ panelViewName: admin-clients and admin-experts → clients (shared)")
else:
    print("⚠️ Could not find panelViewName pattern")

# 5. Fix lifecycle: add admin-clients and admin-experts back to initClients lifecycle
old_clients_lifecycle = "  if (viewName === 'clients') {\n    requestAnimationFrame(() => initClients());\n  } else {\n    destroyClients();\n  }"
new_clients_lifecycle = "  if (viewName === 'clients' || viewName === 'admin-clients' || viewName === 'admin-experts') {\n    requestAnimationFrame(() => initClients());\n  } else {\n    destroyClients();\n  }"
if old_clients_lifecycle in router:
    router = router.replace(old_clients_lifecycle, new_clients_lifecycle, 1)
    print("✅ Lifecycle: admin-clients and admin-experts trigger initClients")
else:
    print("⚠️ Could not find clients lifecycle pattern")

# 6. Clean up admin lifecycle - remove the empty else branch
old_admin_lifecycle = """  // Admin views lifecycle
  if (viewName === 'admin-overview') {
    import('./views/admin/admin.js').then(m => m.initAdminOverview ? m.initAdminOverview() : null);
  } else {
    // Only admin-overview admin-clients and admin-experts are now using the shared view
  }"""

new_admin_lifecycle = """  // Admin views lifecycle
  if (viewName === 'admin-overview') {
    import('./views/admin/admin.js').then(m => m.initAdminOverview ? m.initAdminOverview() : null);
  }"""

if old_admin_lifecycle in router:
    router = router.replace(old_admin_lifecycle, new_admin_lifecycle, 1)
    print("✅ Lifecycle: cleaned up admin lifecycle (removed empty else)")
else:
    print("⚠️ Could not find old admin lifecycle")

with open('src/router.ts', 'w', encoding='utf-8') as f:
    f.write(router)

print("\n✅ Done! Admin role preserved when clicking Clients or Experts.")
