"""
Simplified fix for admin views:
1. Add view-admin-overview (rich dashboard)
2. Add view-admin-clients (simplified user list, not full clients copy)
3. Add view-admin-settings (restore)
4. Fix admin sidebar
5. Fix router
"""
import re

# Read files
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ══════════════════════════════════════════════════════════════
# Find view-clients to extract it for admin copy
# ══════════════════════════════════════════════════════════════
# Simple approach: find by line
lines = content.splitlines()
start = None
for i, line in enumerate(lines):
    if 'id="view-clients"' in line and 'class="view-panel"' in line:
        start = i
        break

if start is None:
    print("❌ view-clients not found")
    # Fall back to content search
    idx = content.find('id="view-clients"')
    if idx > 0:
        # Find section start
        section_start = content.rfind('<section', 0, idx)
        if section_start > 0:
            # Find next view-panel
            next_view = content.find('class="view-panel"', idx + 50)
            # Find the section end by tracking nesting
            section_content = content[section_start:]
            # Find closing section
            depth = 1
            i = section_content.find('>', 50) + 1
            while i < len(section_content) and depth > 0:
                next_open = section_content.find('<section', i)
                next_close = section_content.find('</section>', i)
                if next_close == -1:
                    break
                if next_open != -1 and next_open < next_close:
                    depth += 1
                    i = section_content.find('>', next_open) + 1
                else:
                    depth -= 1
                    i = next_close + 10
            clients_html = section_content[:i]
            print(f"✅ Extracted view-clients via content search ({len(clients_html)} chars)")
        else:
            print("❌ Could not find section start")
            clients_html = '<section class="view-panel" id="view-clients"><div>Clients</div></section>'
    else:
        print("❌ view-clients id not found at all")
        clients_html = '<section class="view-panel" id="view-clients"><div>Clients</div></section>'
else:
    # Find end
    end = len(lines)
    for j in range(start+1, len(lines)):
        if 'class="view-panel"' in lines[j]:
            end = j
            break
    clients_html = '\n'.join(lines[start:end])
    print(f"✅ Extracted view-clients via lines ({len(clients_html)} chars)")

# Create admin clients copy with unique IDs
admin_clients_html = clients_html.replace('id="view-clients"', 'id="view-admin-clients"')

# Prefix critical IDs
id_prefixes = [
    'clientsSearch', 'clientsAddBtn', 'clientsTableBody',
    'clientsDetailPanel', 'cdpBackBtn', 'cdpAvatar', 'cdpName',
    'cdpStatus', 'cdpEditToggle', 'cdpEvaluateBtn',
    'cdpFieldCivility', 'cdpFieldFirstname', 'cdpFieldLastname',
    'cdpFieldEmail', 'cdpFieldPhone', 'cdpFieldAddress',
    'cdpFieldCp', 'cdpFieldCity',
    'cdpOvScore', 'cdpStatusToggle', 'cdpStatusDropdown', 'cdpStatusMenu',
]
for pid in id_prefixes:
    admin_clients_html = admin_clients_html.replace(f'id="{pid}"', f'id="Admin{pid[0].upper()}{pid[1:]}"')
    admin_clients_html = admin_clients_html.replace(f'#{pid}', f'#Admin{pid[0].upper()}{pid[1:]}')

admin_clients_html = '        <!-- ADMIN CLIENTS -->\n' + admin_clients_html

# ══════════════════════════════════════════════════════════════
# Admin dashboard
# ══════════════════════════════════════════════════════════════
admin_overview_html = '''
        <!-- ADMIN DASHBOARD -->
        <section class="view-panel" id="view-admin-overview">
          <section class="banner-section">
            <div class="banner-card">
              <div class="banner-gallery">
                <img class="banner-gallery-slide" src="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200&q=50" alt="" loading="lazy" />
                <img class="banner-gallery-slide" src="https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1200&q=50" alt="" loading="lazy" />
                <img class="banner-gallery-slide" src="https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&q=50" alt="" loading="lazy" />
              </div>
              <div class="banner-info">
                <h1>Administration<br>Plateforme Typhoon</h1>
                <p id="adminBannerInfo">Supervision des utilisateurs, biens et evaluations</p>
              </div>
              <div class="banner-completion-card">
                <div class="completion-header">
                  <div><span class="completion-label">Plateforme</span><h2 id="adminBannerScore">—</h2></div>
                  <span class="trend-indicator positive" id="adminBannerTrend">Operationnel</span>
                </div>
                <div class="sparkline-chart">
                  <svg viewBox="0 0 200 80" preserveAspectRatio="none">
                    <defs><linearGradient id="adminChartGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="rgba(99,102,241,0.4)"/><stop offset="100%" stop-color="rgba(99,102,241,0.0)"/></linearGradient></defs>
                    <path d="M 0,60 Q 30,45 60,35 T 120,45 T 160,20 T 200,30" fill="none" stroke="#6366f1" stroke-width="2.5" stroke-linecap="round"/>
                    <path d="M 0,60 Q 30,45 60,35 T 120,45 T 160,20 T 200,30 L 200,80 L 0,80 Z" fill="url(#adminChartGrad)"/>
                    <circle cx="160" cy="20" r="4" fill="#6366f1" stroke="rgba(99,102,241,0.5)" stroke-width="3"/>
                  </svg>
                </div>
                <div class="completion-footer">
                  <div class="footer-stat"><span class="footer-stat-label" id="adminFooterUsers">0 utilisateurs</span></div>
                  <div class="segmented-progress"><span class="seg active"></span><span class="seg active"></span><span class="seg active"></span><span class="seg"></span><span class="seg"></span></div>
                  <div class="footer-stat align-right"><span class="footer-stat-label" id="adminFooterActive">0 actifs</span></div>
                </div>
              </div>
            </div>
          </section>
          <section class="widgets-grid">
            <div class="grid-column col-span-2">
              <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:12px;">
                <div class="dashboard-card" style="padding:14px;"><span class="material-symbols-outlined" style="font-size:18px;color:#6366f1;">group</span><span class="stat-card-value" style="font-size:22px;font-weight:600;display:block;" id="adminStatOverviewUsers">0</span><span class="stat-card-label" style="font-size:10px;color:var(--text-muted);">Utilisateurs</span></div>
                <div class="dashboard-card" style="padding:14px;"><span class="material-symbols-outlined" style="font-size:18px;color:#10b981;">home</span><span class="stat-card-value" style="font-size:22px;font-weight:600;display:block;" id="adminStatOverviewProps">0</span><span class="stat-card-label" style="font-size:10px;color:var(--text-muted);">Biens</span></div>
                <div class="dashboard-card" style="padding:14px;"><span class="material-symbols-outlined" style="font-size:18px;color:#f59e0b;">assessment</span><span class="stat-card-value" style="font-size:22px;font-weight:600;display:block;" id="adminStatOverviewAssess">0</span><span class="stat-card-label" style="font-size:10px;color:var(--text-muted);">Evaluations</span></div>
              </div>
              <div class="dashboard-card">
                <div class="card-header"><h3>Activité recente</h3><span class="material-symbols-outlined action-icon">north_east</span></div>
                <div class="card-body">
                  <div id="adminActivityTimeline" style="display:flex;flex-direction:column;gap:8px;">
                    <div class="activity-item" style="padding:8px 0;border-bottom:1px solid var(--border-color);font-size:13px;color:var(--text-secondary);display:flex;align-items:center;gap:8px;"><span class="material-symbols-outlined" style="font-size:16px;color:#6366f1;">person_add</span><span>Nouvel assureur inscrit : <strong>Sophie Martin</strong></span><span style="margin-left:auto;font-size:11px;color:var(--text-muted);">Il y a 2h</span></div>
                    <div class="activity-item" style="padding:8px 0;border-bottom:1px solid var(--border-color);font-size:13px;color:var(--text-secondary);display:flex;align-items:center;gap:8px;"><span class="material-symbols-outlined" style="font-size:16px;color:#10b981;">home</span><span>Nouveau bien ajoute : <strong>15 Rue de Lille, Paris</strong></span><span style="margin-left:auto;font-size:11px;color:var(--text-muted);">Il y a 5h</span></div>
                    <div class="activity-item" style="padding:8px 0;font-size:13px;color:var(--text-secondary);display:flex;align-items:center;gap:8px;"><span class="material-symbols-outlined" style="font-size:16px;color:#f59e0b;">assessment</span><span>Evaluation completee pour <strong>Jean Dupont</strong></span><span style="margin-left:auto;font-size:11px;color:var(--text-muted);">Il y a 1j</span></div>
                  </div>
                </div>
              </div>
            </div>
            <div class="grid-column col-span-3">
              <div class="dashboard-card">
                <div class="card-header"><h3>Repartition par role</h3><span class="material-symbols-outlined action-icon">north_east</span></div>
                <div class="card-body">
                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:8px 0;">
                    <div style="text-align:center;padding:16px;background:var(--bg-panel);border-radius:12px;"><span class="material-symbols-outlined" style="font-size:32px;color:#c56a3d;">badge</span><div style="font-size:28px;font-weight:700;margin:4px 0;" id="adminStatRoleAssureurs">3</div><div style="font-size:12px;color:var(--text-muted);">Assureurs</div></div>
                    <div style="text-align:center;padding:16px;background:var(--bg-panel);border-radius:12px;"><span class="material-symbols-outlined" style="font-size:32px;color:#10b981;">person_pin</span><div style="font-size:28px;font-weight:700;margin:4px 0;" id="adminStatRoleAssures">4</div><div style="font-size:12px;color:var(--text-muted);">Assures</div></div>
                    <div style="text-align:center;padding:16px;background:var(--bg-panel);border-radius:12px;"><span class="material-symbols-outlined" style="font-size:32px;color:#8b5cf6;">build</span><div style="font-size:28px;font-weight:700;margin:4px 0;" id="adminStatRoleExperts">2</div><div style="font-size:12px;color:var(--text-muted);">Experts</div></div>
                    <div style="text-align:center;padding:16px;background:var(--bg-panel);border-radius:12px;"><span class="material-symbols-outlined" style="font-size:32px;color:#3b82f6;">admin_panel_settings</span><div style="font-size:28px;font-weight:700;margin:4px 0;" id="adminStatRoleAdmins">1</div><div style="font-size:12px;color:var(--text-muted);">Admins</div></div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </section>
'''

admin_settings_html = '''
        <!-- ADMIN SETTINGS -->
        <section class="view-panel" id="view-admin-settings">
          <div class="settings-container" style="padding:16px 0;">
            <div class="settings-tabs" id="adminSettingsTabs" style="display:flex;gap:0;border-bottom:1px solid var(--border-color);margin-bottom:20px;">
              <button class="settings-tab active" data-stab="general">General</button>
              <button class="settings-tab" data-stab="security">Securite</button>
              <button class="settings-tab" data-stab="notifications">Notifications</button>
            </div>
            <div class="settings-content active" data-scontent="general">
              <div class="dashboard-card" style="padding:20px;">
                <h4 style="font-size:14px;font-weight:600;margin-bottom:16px;">Configuration generale</h4>
                <div class="settings-field"><label style="font-size:12px;color:var(--text-secondary);display:block;margin-bottom:4px;">Nom de la plateforme</label><input type="text" value="Typhoon — Risk Platform" class="afi-input" style="max-width:360px;"></div>
                <div class="settings-field" style="margin-top:12px;"><label style="font-size:12px;color:var(--text-secondary);display:block;margin-bottom:4px;">Email support</label><input type="email" value="support@typhoon.fr" class="afi-input" style="max-width:360px;"></div>
              </div>
            </div>
            <div class="settings-content" data-scontent="security"><div class="dashboard-card" style="padding:20px;"><h4 style="font-size:14px;font-weight:600;margin-bottom:16px;">Politique de securite</h4><p style="font-size:13px;color:var(--text-secondary);">Configurations de securite — a implementer.</p></div></div>
            <div class="settings-content" data-scontent="notifications"><div class="dashboard-card" style="padding:20px;"><h4 style="font-size:14px;font-weight:600;margin-bottom:16px;">Notifications systeme</h4><p style="font-size:13px;color:var(--text-secondary);">Preferences de notification — a implementer.</p></div></div>
          </div>
        </section>
'''

# ══════════════════════════════════════════════════════════════
# Insert all admin views before </main>
# ══════════════════════════════════════════════════════════════
all_admin = admin_overview_html + '\n' + admin_clients_html + '\n' + admin_settings_html

if '</main>' in content:
    content = content.replace('</main>', all_admin + '\n      </main>', 1)
    print("✅ Admin views inserted")
else:
    print("❌ Could not find </main>")
    exit(1)

# ══════════════════════════════════════════════════════════════
# Fix admin sidebar: all buttons use admin-* views
# ══════════════════════════════════════════════════════════════
fixes = [
    ('nav-role-admin" data-view="overview"', 'nav-role-admin" data-view="admin-overview"'),
    ('nav-role-admin" data-view="clients"', 'nav-role-admin" data-view="admin-clients"'),
    ('nav-role-admin" data-view="settings"', 'nav-role-admin" data-view="admin-settings"'),
]
for old, new in fixes:
    if old in content:
        content = content.replace(old, new, 1)
        print(f"✅ Sidebar fix: {old}")
    else:
        print(f"⚠️ Not found: {old}")

# Write HTML
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ HTML written")

# ══════════════════════════════════════════════════════════════
# Update router
# ══════════════════════════════════════════════════════════════
with open('src/router.ts', 'r', encoding='utf-8') as f:
    router = f.read()

# VIEW_TABS
router = router.replace(
    "  // Admin views\n  'admin-users': [],",
    "  // Admin views\n  'admin-overview': [],\n  'admin-users': [],\n  'admin-clients': [],\n  'admin-settings': [],"
)

# ROUTES
router = router.replace(
    "  // Admin routes — overview uses shared view; admin-users is separate\n  'admin-users': '/admin/users',",
    "  // Admin routes\n  'admin-overview': '/admin/overview',\n  'admin-users': '/admin/users',\n  'admin-clients': '/admin/clients',\n  'admin-settings': '/admin/settings',"
)

# URL parsing
router = router.replace(
    "const map: Record<string, string> = { overview: 'overview', users: 'admin-users', clients: 'clients', settings: 'settings' };",
    "const map: Record<string, string> = { overview: 'admin-overview', users: 'admin-users', clients: 'admin-clients', settings: 'admin-settings' };"
)

# Lifecycle for admin-overview
router = router.replace(
    "  // Admin views lifecycle\n  if (viewName === 'admin-users') {",
    "  // Admin views lifecycle\n  if (viewName === 'admin-overview') {\n    import('./views/admin/admin.js').then(m => m.initAdminOverview ? m.initAdminOverview() : null);\n  } else if (viewName === 'admin-users') {"
)

# admin-clients lifecycle (delegate to initClients)
router = router.replace(
    "  if (viewName === 'clients') {\n    requestAnimationFrame(() => initClients());\n  }",
    "  if (viewName === 'clients' || viewName === 'admin-clients') {\n    requestAnimationFrame(() => initClients());\n  }"
)

# panelViewName mapping - remove admin redirect
old_map = "const panelViewName = viewName === 'assureur-settings' || viewName === 'assure-settings' ? 'settings'\n    : viewName === 'admin-clients' ? 'clients'\n    : viewName;"
new_map = "const panelViewName = viewName === 'assureur-settings' || viewName === 'assure-settings' ? 'settings'\n    : viewName;"
if old_map in router:
    router = router.replace(old_map, new_map, 1)
    print("✅ panelViewName fixed (removed admin redirect)")
elif 'admin-clients' not in router:
    print("✅ panelViewName already clean")

with open('src/router.ts', 'w', encoding='utf-8') as f:
    f.write(router)

print("✅ Router updated!")

# ══════════════════════════════════════════════════════════════
# Update admin.ts to also export initAdminOverview
# ══════════════════════════════════════════════════════════════
with open('src/views/admin/admin.ts', 'r', encoding='utf-8') as f:
    admin_ts = f.read()

# Add initAdminOverview that delegates to the existing overview module
if 'initAdminOverview' not in admin_ts:
    admin_ts = admin_ts.replace(
        'export function initAdminUsers',
        "export function initAdminOverview(): void {\n"
        "  // Delegate to shared overview module\n"
        "  import('../overview/overview.js').then(m => m.initOverview ? m.initOverview() : null);\n"
        "}\n"
        "export function destroyAdminOverview(): void {\n"
        "  import('../overview/overview.js').then(m => m.destroyOverview ? m.destroyOverview() : null);\n"
        "}\n\n"
        "export function initAdminUsers"
    )
    with open('src/views/admin/admin.ts', 'w', encoding='utf-8') as f:
        f.write(admin_ts)
    print("✅ admin.ts: added initAdminOverview/destroyAdminOverview")
else:
    print("⏭️ initAdminOverview already exists")

print("\n✅ All done!")
