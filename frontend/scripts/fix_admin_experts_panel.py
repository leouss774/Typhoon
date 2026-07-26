"""
Give admin-experts its own panel (same layout style as clients, but for experts).
Remove it from panelViewName mapping.
"""
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Create expert management panel HTML with unique IDs matching admin.ts targets
experts_panel = '''        <!-- ADMIN EXPERTS — Expert Management -->
        <section class="view-panel" id="view-admin-experts">
          <div style="display:flex;align-items:center;justify-content:space-between;padding:16px 0 8px;gap:12px;flex-wrap:wrap;">
            <h2 style="font-size:18px;font-weight:600;margin:0;">Gestion des experts</h2>
            <div style="display:flex;gap:8px;align-items:center;">
              <div style="position:relative;">
                <span class="material-symbols-outlined" style="position:absolute;left:10px;top:50%;transform:translateY(-50%);font-size:16px;color:var(--text-muted);pointer-events:none;">search</span>
                <input type="text" id="adminExpertSearch" placeholder="Rechercher un expert..." style="padding:7px 10px 7px 32px;border:1px solid var(--border-color);border-radius:8px;background:var(--bg-panel);color:var(--text-primary);font-size:13px;width:220px;outline:none;font-family:var(--font-primary);">
              </div>
              <button id="adminAddExpertBtn" style="display:flex;align-items:center;gap:6px;padding:7px 14px;border:none;border-radius:8px;background:var(--color-primary);color:#fff;font-size:13px;font-weight:500;cursor:pointer;font-family:var(--font-primary);transition:opacity 0.15s;">
                <span class="material-symbols-outlined" style="font-size:16px;">add</span> Inviter
              </button>
            </div>
          </div>
          <div class="dashboard-card" style="overflow:hidden;">
            <table style="width:100%;border-collapse:collapse;font-size:13px;">
              <thead>
                <tr style="background:var(--bg-panel);border-bottom:1px solid var(--border-color);">
                  <th style="padding:10px 14px;text-align:left;font-weight:500;color:var(--text-secondary);font-size:11px;text-transform:uppercase;letter-spacing:0.5px;">Nom</th>
                  <th style="padding:10px 14px;text-align:left;font-weight:500;color:var(--text-secondary);font-size:11px;text-transform:uppercase;letter-spacing:0.5px;">Email</th>
                  <th style="padding:10px 14px;text-align:left;font-weight:500;color:var(--text-secondary);font-size:11px;text-transform:uppercase;letter-spacing:0.5px;">Spécialité</th>
                  <th style="padding:10px 14px;text-align:left;font-weight:500;color:var(--text-secondary);font-size:11px;text-transform:uppercase;letter-spacing:0.5px;">Statut</th>
                  <th style="padding:10px 14px;text-align:left;font-weight:500;color:var(--text-secondary);font-size:11px;text-transform:uppercase;letter-spacing:0.5px;">Actions</th>
                </tr>
              </thead>
              <tbody id="adminExpertTableBody">
                <tr><td colspan="5" style="padding:24px;text-align:center;color:var(--text-muted);font-size:13px;">Chargement des experts...</td></tr>
              </tbody>
            </table>
          </div>
          <!-- Quick stats row -->
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:12px;">
            <div class="dashboard-card" style="padding:12px;text-align:center;"><div style="font-size:22px;font-weight:600;" id="adminExpertStatTotal">—</div><div style="font-size:10px;color:var(--text-muted);">Total</div></div>
            <div class="dashboard-card" style="padding:12px;text-align:center;"><div style="font-size:22px;font-weight:600;color:#10b981;" id="adminExpertStatActive">—</div><div style="font-size:10px;color:var(--text-muted);">Actifs</div></div>
            <div class="dashboard-card" style="padding:12px;text-align:center;"><div style="font-size:22px;font-weight:600;color:#f59e0b;" id="adminExpertStatPending">—</div><div style="font-size:10px;color:var(--text-muted);">En attente</div></div>
            <div class="dashboard-card" style="padding:12px;text-align:center;"><div style="font-size:22px;font-weight:600;color:#8b5cf6;" id="adminExpertStatMissions">—</div><div style="font-size:10px;color:var(--text-muted);">Missions</div></div>
          </div>
        </section>
'''

# Insert before view-admin-overview
# Find view-admin-overview section
idx = html.find('id="view-admin-overview"')
if idx > 0:
    section_start = html.rfind('<section', 0, idx)
    html = html[:section_start] + experts_panel + '\n        ' + html[section_start:]
    print("✅ Inserted view-admin-experts panel before admin-overview")
else:
    print("⚠️ Could not find view-admin-overview, inserting at end")
    html = html.replace('</main>', experts_panel + '\n      </main>', 1)
    print("✅ Inserted view-admin-experts panel before </main>")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# ══════════════════════════════════════════════════════════════
# Fix router
# ══════════════════════════════════════════════════════════════
with open('src/router.ts', 'r', encoding='utf-8') as f:
    router = f.read()

# 1. Remove admin-experts from panelViewName mapping
router = router.replace(
    "    : viewName === 'admin-clients' || viewName === 'admin-experts' || viewName === 'expert-clients' ? 'clients'",
    "    : viewName === 'admin-clients' || viewName === 'expert-clients' ? 'clients'",
    1
)
print("✅ panelViewName: removed admin-experts from clients redirect")

# 2. Remove admin-experts from initClients lifecycle
router = router.replace(
    "if (viewName === 'clients' || viewName === 'admin-clients' || viewName === 'admin-experts' || viewName === 'expert-clients') {",
    "if (viewName === 'clients' || viewName === 'admin-clients' || viewName === 'expert-clients') {",
    1
)
print("✅ Lifecycle: removed admin-experts from initClients")

# 3. Add dedicated admin-experts lifecycle in the admin section
old_admin_lifecycle = """  // Admin views lifecycle
  if (viewName === 'admin-overview') {
    import('./views/admin/admin.js').then(m => m.initAdminOverview ? m.initAdminOverview() : null);
  }"""

new_admin_lifecycle = """  // Admin views lifecycle
  if (viewName === 'admin-overview') {
    import('./views/admin/admin.js').then(m => m.initAdminOverview ? m.initAdminOverview() : null);
  } else if (viewName === 'admin-experts') {
    import('./views/admin/admin.js').then(m => m.initAdminExperts ? m.initAdminExperts() : null);
  }"""

if old_admin_lifecycle in router:
    router = router.replace(old_admin_lifecycle, new_admin_lifecycle, 1)
    print("✅ Lifecycle: added dedicated admin-experts → initAdminExperts")
else:
    print("⚠️ Could not find admin lifecycle pattern")

with open('src/router.ts', 'w', encoding='utf-8') as f:
    f.write(router)

# Verify
with open('index.html', 'r', encoding='utf-8') as f:
    verify = f.read()
count = verify.count('adminExpertTableBody')
print(f"✅ adminExpertTableBody occurrences: {count}")

print("\n✅ Done! admin-experts now has its own panel with expert data.")
