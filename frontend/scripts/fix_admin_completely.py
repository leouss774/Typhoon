"""
Complete fix for admin:
1. Restore view-admin-overview (rich dashboard)
2. Restore view-admin-clients (with unique IDs)
3. Restore view-admin-settings (inline tabs)
4. Fix admin sidebar: all buttons point to admin-* views
5. Fix router: add admin-overview, admin-clients, admin-settings
"""
import re, os

CURRENT = 'index.html'
ROUTER = 'src/router.ts'

with open(CURRENT, 'r', encoding='utf-8') as f:
    content = f.read()

# ══════════════════════════════════════════════════════════════
# 1. ADMIN OVERVIEW — Rich dashboard (modeled after view-overview)
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
                <p id="adminBannerInfo">Supervision des utilisateurs, biens et évaluations</p>
              </div>
              <div class="banner-completion-card">
                <div class="completion-header">
                  <div>
                    <span class="completion-label">Plateforme</span>
                    <h2 id="adminBannerScore">—</h2>
                  </div>
                  <span class="trend-indicator positive" id="adminBannerTrend">Opérationnel</span>
                </div>
                <div class="sparkline-chart">
                  <svg viewBox="0 0 200 80" preserveAspectRatio="none">
                    <defs>
                      <linearGradient id="adminChartGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stop-color="rgba(99,102,241,0.4)" />
                        <stop offset="100%" stop-color="rgba(99,102,241,0.0)" />
                      </linearGradient>
                    </defs>
                    <path d="M 0,60 Q 30,45 60,35 T 120,45 T 160,20 T 200,30" fill="none" stroke="#6366f1" stroke-width="2.5" stroke-linecap="round"/>
                    <path d="M 0,60 Q 30,45 60,35 T 120,45 T 160,20 T 200,30 L 200,80 L 0,80 Z" fill="url(#adminChartGrad)"/>
                    <circle cx="160" cy="20" r="4" fill="#6366f1" stroke="rgba(99,102,241,0.5)" stroke-width="3"/>
                  </svg>
                </div>
                <div class="completion-footer">
                  <div class="footer-stat">
                    <span class="footer-stat-label" id="adminFooterUsers">0 utilisateurs</span>
                  </div>
                  <div class="segmented-progress">
                    <span class="seg active"></span>
                    <span class="seg active"></span>
                    <span class="seg active"></span>
                    <span class="seg"></span>
                    <span class="seg"></span>
                  </div>
                  <div class="footer-stat align-right">
                    <span class="footer-stat-label" id="adminFooterActive">0 actifs</span>
                  </div>
                </div>
              </div>
            </div>
          </section>
          <section class="widgets-grid">
            <div class="grid-column col-span-2">
              <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:12px;">
                <div class="dashboard-card" style="padding:14px;">
                  <span class="material-symbols-outlined" style="font-size:18px;color:#6366f1;">group</span>
                  <span class="stat-card-value" style="font-size:22px;font-weight:600;display:block;" id="adminStatOverviewUsers">0</span>
                  <span class="stat-card-label" style="font-size:10px;color:var(--text-muted);">Utilisateurs</span>
                </div>
                <div class="dashboard-card" style="padding:14px;">
                  <span class="material-symbols-outlined" style="font-size:18px;color:#10b981;">home</span>
                  <span class="stat-card-value" style="font-size:22px;font-weight:600;display:block;" id="adminStatOverviewProps">0</span>
                  <span class="stat-card-label" style="font-size:10px;color:var(--text-muted);">Biens</span>
                </div>
                <div class="dashboard-card" style="padding:14px;">
                  <span class="material-symbols-outlined" style="font-size:18px;color:#f59e0b;">assessment</span>
                  <span class="stat-card-value" style="font-size:22px;font-weight:600;display:block;" id="adminStatOverviewAssess">0</span>
                  <span class="stat-card-label" style="font-size:10px;color:var(--text-muted);">Évaluations</span>
                </div>
              </div>
              <div class="dashboard-card cross-section-card">
                <div class="card-header">
                  <h3>Activité récente</h3>
                  <span class="material-symbols-outlined action-icon">north_east</span>
                </div>
                <div class="card-body">
                  <div id="adminActivityTimeline" style="display:flex;flex-direction:column;gap:8px;">
                    <div class="activity-item" style="padding:8px 0;border-bottom:1px solid var(--border-color);font-size:13px;color:var(--text-secondary);display:flex;align-items:center;gap:8px;">
                      <span class="material-symbols-outlined" style="font-size:16px;color:#6366f1;">person_add</span>
                      <span>Nouvel assureur inscrit : <strong>Sophie Martin</strong></span>
                      <span style="margin-left:auto;font-size:11px;color:var(--text-muted);">Il y a 2h</span>
                    </div>
                    <div class="activity-item" style="padding:8px 0;border-bottom:1px solid var(--border-color);font-size:13px;color:var(--text-secondary);display:flex;align-items:center;gap:8px;">
                      <span class="material-symbols-outlined" style="font-size:16px;color:#10b981;">home</span>
                      <span>Nouveau bien ajouté : <strong>15 Rue de Lille, Paris</strong></span>
                      <span style="margin-left:auto;font-size:11px;color:var(--text-muted);">Il y a 5h</span>
                    </div>
                    <div class="activity-item" style="padding:8px 0;font-size:13px;color:var(--text-secondary);display:flex;align-items:center;gap:8px;">
                      <span class="material-symbols-outlined" style="font-size:16px;color:#f59e0b;">assessment</span>
                      <span>Évaluation complétée pour <strong>Jean Dupont</strong></span>
                      <span style="margin-left:auto;font-size:11px;color:var(--text-muted);">Il y a 1j</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="grid-column col-span-3">
              <div class="dashboard-card">
                <div class="card-header">
                  <h3>Répartition par rôle</h3>
                  <span class="material-symbols-outlined action-icon">north_east</span>
                </div>
                <div class="card-body">
                  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:8px 0;">
                    <div class="stat-role-card" style="text-align:center;padding:16px;background:var(--bg-panel);border-radius:12px;">
                      <span class="material-symbols-outlined" style="font-size:32px;color:#c56a3d;">badge</span>
                      <div style="font-size:28px;font-weight:700;margin:4px 0;" id="adminStatRoleAssureurs">3</div>
                      <div style="font-size:12px;color:var(--text-muted);">Assureurs</div>
                    </div>
                    <div class="stat-role-card" style="text-align:center;padding:16px;background:var(--bg-panel);border-radius:12px;">
                      <span class="material-symbols-outlined" style="font-size:32px;color:#10b981;">person_pin</span>
                      <div style="font-size:28px;font-weight:700;margin:4px 0;" id="adminStatRoleAssures">4</div>
                      <div style="font-size:12px;color:var(--text-muted);">Assurés</div>
                    </div>
                    <div class="stat-role-card" style="text-align:center;padding:16px;background:var(--bg-panel);border-radius:12px;">
                      <span class="material-symbols-outlined" style="font-size:32px;color:#8b5cf6;">build</span>
                      <div style="font-size:28px;font-weight:700;margin:4px 0;" id="adminStatRoleExperts">2</div>
                      <div style="font-size:12px;color:var(--text-muted);">Experts</div>
                    </div>
                    <div class="stat-role-card" style="text-align:center;padding:16px;background:var(--bg-panel);border-radius:12px;">
                      <span class="material-symbols-outlined" style="font-size:32px;color:#3b82f6;">admin_panel_settings</span>
                      <div style="font-size:28px;font-weight:700;margin:4px 0;" id="adminStatRoleAdmins">1</div>
                      <div style="font-size:12px;color:var(--text-muted);">Admins</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </section>
'''

# ══════════════════════════════════════════════════════════════
# 2. ADMIN CLIENTS — Copy of view-clients with unique admin-prefixed IDs
# ══════════════════════════════════════════════════════════════
# First, extract view-clients
def extract_section(html, view_id):
    pattern = view_id + '"'
    idx = html.find(pattern)
    if idx == -1:
        return None
    # Find the section start
    start = html.rfind('<section', 0, idx)
    if start == -1:
        return None
    # Track nesting to find closing
    i = html.find('>', idx) + 1
    depth = 1
    while i < len(html) and depth > 0:
        next_open = html.find('<section', i)
        next_close = html.find('</section>', i)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            i = html.find('>', next_open) + 1
        else:
            depth -= 1
            i = next_close + 10
    return html[start:i]

clients_html = extract_section(content, 'id="view-clients"')
if not clients_html:
    print("❌ Could not extract view-clients")
    exit(1)

# Create admin clients copy with unique IDs
admin_clients_html = clients_html.replace('id="view-clients"', 'id="view-admin-clients"')
# Prefix all critical IDs with 'admin'
id_prefixes = [
    'clientsSearch', 'clientsAddBtn', 'clientsTableBody', 
    'clientsDetailPanel', 'cdpBackBtn', 'cdpAvatar', 'cdpName',
    'cdpStatus', 'cdpEditToggle', 'cdpEvaluateBtn',
    'cdpFieldCivility', 'cdpFieldFirstname', 'cdpFieldLastname',
    'cdpFieldEmail', 'cdpFieldPhone', 'cdpFieldAddress',
    'cdpFieldCp', 'cdpFieldCity', 'cdpSaveBtn', 'cdpCancelBtn',
    'cdpFormActions', 'cdpStatusToggle', 'cdpStatusDropdown',
    'cdpStatusMenu', 'cdpOvCivility', 'cdpOvName', 'cdpOvEmail',
    'cdpOvPhone', 'cdpOvAddress', 'cdpOvCity', 'cdpOvScore',
    'cdpTabOverview', 'cdpTabInfo', 'cdpTabContracts', 'cdpTabPayments',
    'clientNotificationBadge',
]
for pid in id_prefixes:
    admin_clients_html = admin_clients_html.replace(f'id="{pid}"', f'id="admin{pid[0].upper()}{pid[1:]}"')
    admin_clients_html = admin_clients_html.replace(f'id=\\"{pid}\\"', f'id=\\"admin{pid[0].upper()}{pid[1:]}\\"')
    # Also replace hash references
    admin_clients_html = admin_clients_html.replace(f'#{pid}', f'#admin{pid[0].upper()}{pid[1:]}')

admin_clients_html = '        <!-- ADMIN CLIENTS -->\n' + admin_clients_html

# ══════════════════════════════════════════════════════════════
# 3. ADMIN SETTINGS — restore with inline tabs
# ══════════════════════════════════════════════════════════════
admin_settings_html = '''
        <!-- ADMIN SETTINGS -->
        <section class="view-panel" id="view-admin-settings">
          <div class="settings-container" style="padding:16px 0;">
            <div class="settings-tabs" id="adminSettingsTabs" style="display:flex;gap:0;border-bottom:1px solid var(--border-color);margin-bottom:20px;">
              <button class="settings-tab active" data-stab="general">Général</button>
              <button class="settings-tab" data-stab="security">Sécurité</button>
              <button class="settings-tab" data-stab="notifications">Notifications</button>
            </div>
            <div class="settings-content active" data-scontent="general">
              <div class="dashboard-card" style="padding:20px;">
                <h4 style="font-size:14px;font-weight:600;margin-bottom:16px;">Configuration générale</h4>
                <div class="settings-field"><label style="font-size:12px;color:var(--text-secondary);display:block;margin-bottom:4px;">Nom de la plateforme</label><input type="text" value="Typhoon — Risk Platform" class="afi-input" style="max-width:360px;"></div>
                <div class="settings-field" style="margin-top:12px;"><label style="font-size:12px;color:var(--text-secondary);display:block;margin-bottom:4px;">Email support</label><input type="email" value="support@typhoon.fr" class="afi-input" style="max-width:360px;"></div>
                <button class="risk-btn primary" style="margin-top:16px;height:34px;font-size:13px;">Sauvegarder</button>
              </div>
            </div>
            <div class="settings-content" data-scontent="security">
              <div class="dashboard-card" style="padding:20px;">
                <h4 style="font-size:14px;font-weight:600;margin-bottom:16px;">Politique de sécurité</h4>
                <p style="font-size:13px;color:var(--text-secondary);">Configurations de sécurité — à implémenter.</p>
              </div>
            </div>
            <div class="settings-content" data-scontent="notifications">
              <div class="dashboard-card" style="padding:20px;">
                <h4 style="font-size:14px;font-weight:600;margin-bottom:16px;">Notifications système</h4>
                <p style="font-size:13px;color:var(--text-secondary);">Préférences de notification — à implémenter.</p>
              </div>
            </div>
          </div>
        </section>
'''

# ══════════════════════════════════════════════════════════════
# INSERT ALL ADMIN VIEWS after the EXPERT VIEWS section
# ══════════════════════════════════════════════════════════════
# Find the end of expert views (just before </main>)
all_admin_html = admin_overview_html + admin_clients_html + admin_settings_html

# Insert before </main>
if '</main>' in content:
    content = content.replace('</main>', all_admin_html + '\n      </main>', 1)
    print("✅ Admin views (overview + clients + settings) inserted")
else:
    print("❌ Could not find </main>")
    exit(1)

# ══════════════════════════════════════════════════════════════
# FIX ADMIN SIDEBAR — all buttons point to admin-* views
# ══════════════════════════════════════════════════════════════
sidebar_fixes = {
    'data-view="overview" style="display:none;"><span class="material-symbols-outlined">dashboard</span><span class="nav-label">Dashboard</span>': 'data-view="admin-overview" style="display:none;"><span class="material-symbols-outlined">dashboard</span><span class="nav-label">Dashboard</span>',
    'data-view="clients" style="display:none;"><span class="material-symbols-outlined">groups</span><span class="nav-label">Clients</span>': 'data-view="admin-clients" style="display:none;"><span class="material-symbols-outlined">groups</span><span class="nav-label">Clients</span>',
    'data-view="settings" style="display:none;"><span class="material-symbols-outlined">settings</span><span class="nav-label">Paramètres</span>': 'data-view="admin-settings" style="display:none;"><span class="material-symbols-outlined">settings</span><span class="nav-label">Paramètres</span>',
}

for old_btn, new_btn in sidebar_fixes.items():
    # Only replace for admin (nav-role-admin)
    old_admin = f'class="nav-item nav-role-admin" {old_btn}'
    new_admin = f'class="nav-item nav-role-admin" {new_btn}'
    if old_admin in content:
        content = content.replace(old_admin, new_admin, 1)
        print(f"✅ Admin sidebar fix: {old_btn[:50]}...")
    else:
        print(f"⚠️ Could not find admin sidebar button: {old_btn[:50]}...")

# Write HTML
with open(CURRENT, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ HTML updated ({len(content)} chars)")

# ══════════════════════════════════════════════════════════════
# UPDATE ROUTER
# ══════════════════════════════════════════════════════════════
with open(ROUTER, 'r', encoding='utf-8') as f:
    router = f.read()

# Add admin-overview and admin-clients and admin-settings to VIEW_TABS
old_view_tabs = "  // Admin views\n  'admin-users': [],"
new_view_tabs = "  // Admin views\n  'admin-overview': [],\n  'admin-users': [],\n  'admin-clients': [],\n  'admin-settings': [],"
if old_view_tabs in router:
    router = router.replace(old_view_tabs, new_view_tabs, 1)
    print("✅ VIEW_TABS updated")

# Add to ROUTES
old_routes = "  // Admin routes — overview uses shared view; admin-users is separate\n  'admin-users': '/admin/users',"
new_routes = "  // Admin routes\n  'admin-overview': '/admin/overview',\n  'admin-users': '/admin/users',\n  'admin-clients': '/admin/clients',\n  'admin-settings': '/admin/settings',"
if old_routes in router:
    router = router.replace(old_routes, new_routes, 1)
    print("✅ ROUTES updated")

# Update URL parsing for admin
old_parse = "const map: Record<string, string> = { overview: 'overview', users: 'admin-users', clients: 'clients', settings: 'settings' };"
new_parse = "const map: Record<string, string> = { overview: 'admin-overview', users: 'admin-users', clients: 'admin-clients', settings: 'admin-settings' };"
if old_parse in router:
    router = router.replace(old_parse, new_parse, 1)
    print("✅ URL parsing updated")

# Update setRole for admin (navigate to admin-overview)
old_setrole = "  } else if (role === 'admin' && !activeView.startsWith('admin-')) {\n    navigateTo('admin-overview');"
if old_setrole in router:
    # Keep the navigateTo('admin-overview') since admin-overview now exists
    print("✅ setRole admin already has correct navigation")

# Fix switchView mapping - remove the panelViewName mapping that redirects admin views
old_panel_map = "  // Map all role-specific settings views to shared panel\n  const panelViewName = viewName === 'assureur-settings' || viewName === 'assure-settings' ? 'settings'\n    : viewName;"
# admin-clients and admin-settings now have their own panels, no mapping needed
if old_panel_map in router:
    print("✅ panelViewName already correct (no admin mapping)")

# Add lifecycle for admin-overview, admin-clients, admin-settings
old_lifecycle = "  // Admin views lifecycle\n  if (viewName === 'admin-users') {"
new_lifecycle = "  // Admin views lifecycle\n  if (viewName === 'admin-overview') {\n    import('./views/admin/admin.js').then(m => m.initAdminOverview ? m.initAdminOverview() : null);\n  } else if (viewName === 'admin-users') {"
if old_lifecycle in router:
    router = router.replace(old_lifecycle, new_lifecycle, 1)
    print("✅ Lifecycle updated (admin-overview added)")

# Add admin-clients lifecycle that delegates to initClients
old_clients_lifecycle = "  if (viewName === 'clients') {\n    requestAnimationFrame(() => initClients());\n  }"
new_clients_lifecycle = "  if (viewName === 'clients' || viewName === 'admin-clients') {\n    requestAnimationFrame(() => initClients());\n  }"
if old_clients_lifecycle in router:
    router = router.replace(old_clients_lifecycle, new_clients_lifecycle, 1)
    print("✅ admin-clients lifecycle added (delegates to initClients)")

# Write router
with open(ROUTER, 'w', encoding='utf-8') as f:
    f.write(router)

print("✅ Router updated!")
print("\nDone!")
