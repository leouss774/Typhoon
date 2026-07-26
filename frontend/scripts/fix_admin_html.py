"""
Fix the admin view HTML:
1. Restore the missing settings view opening tag (was eaten by previous script)
2. Rewrite the admin dashboard to use existing brand component patterns
"""
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix settings view - add the proper opening section tag
old_settings_start = '        <!-- ====== VIEW: Admin Settings ====== -->\n          <!-- ACCOUNT sub-tab -->'
new_settings_start = '        <!-- ====== VIEW: Admin Settings ====== -->\n        <section class="view-panel" id="view-settings">\n          <!-- ACCOUNT sub-tab -->'
if old_settings_start in content:
    content = content.replace(old_settings_start, new_settings_start, 1)
    print("[OK] Fixed settings view: added missing <section> wrapper")
else:
    # Try without the commented hint
    old2 = '        <!-- ====== VIEW: Admin Settings ====== -->\n          <div class="settings-tab-content active" data-content="account">'
    new2 = '        <!-- ====== VIEW: Admin Settings ====== -->\n        <section class="view-panel" id="view-settings">\n          <div class="settings-tab-content active" data-content="account">'
    if old2 in content:
        content = content.replace(old2, new2, 1)
        print("[OK] Fixed settings view (v2)")
    else:
        print("[FAIL] Could not find settings view start")

# 2. Now find the end of the settings view - it ends when another view panel starts
# Look for the next view panel marker after the settings section
# The settings section should end with </section> before the </body> tag
# Let's find the correct end
settings_marker = '        <!-- ====== VIEW: Admin Settings ====== -->'
settings_close = content.find('</section>', content.find(settings_marker) + 100)
if settings_close > 0:
    # Add the closing </section> if not already there
    content_before = content[:settings_close+10]
    content_after = content[settings_close+10:]
    # Check if there are more settings tabs
    # Just ensure the settings view is properly closed
    # The settings content likely goes until the </body> tag or another view
    print(f"[OK] Settings view ends at position {settings_close}")

# 3. Rewrite the admin dashboard HTML to use standard design patterns
old_admin_panel_start = '        <!-- ====== VIEW: Admin Dashboard ====== -->\n        <section class="view-panel" id="view-admin-dashboard">'
old_admin_panel_end = '        </section>\n\n        <!-- ====== VIEW: Admin Settings ====== -->'

new_admin_html = '''        <!-- ====== VIEW: Admin Dashboard ====== -->
        <section class="view-panel" id="view-admin-dashboard">
          <!-- Header -->
          <div style="display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:24px;flex-wrap:wrap;">
            <div>
              <h2 style="font-size:20px;font-weight:600;margin:0;color:var(--text-primary);">
                <span class="material-symbols-outlined" style="font-size:24px!important;vertical-align:middle;margin-right:8px;color:var(--color-primary);">admin_panel_settings</span>
                Administration
              </h2>
              <p style="font-size:12px;color:var(--text-muted);margin:4px 0 0;">Vue d\'ensemble de la plateforme</p>
            </div>
          </div>

          <div class="admin-dash-content">
            <!-- Stats cards (matching existing KPI card pattern) -->
            <div class="admin-stats">
              <div class="stat-card">
                <div class="stat-card-icon" style="background:rgba(99,102,241,0.12);color:#6366f1;"><span class="material-symbols-outlined">group</span></div>
                <div class="stat-card-value"><span id="adminStatUsers">0</span></div>
                <div class="stat-card-label">Utilisateurs</div>
              </div>
              <div class="stat-card">
                <div class="stat-card-icon" style="background:rgba(59,130,246,0.12);color:#3b82f6;"><span class="material-symbols-outlined">badge</span></div>
                <div class="stat-card-value"><span id="adminStatAssureurs">0</span></div>
                <div class="stat-card-label">Assureurs</div>
              </div>
              <div class="stat-card">
                <div class="stat-card-icon" style="background:rgba(16,185,129,0.12);color:#10b981;"><span class="material-symbols-outlined">person_pin</span></div>
                <div class="stat-card-value"><span id="adminStatAssures">0</span></div>
                <div class="stat-card-label">Assures</div>
              </div>
              <div class="stat-card">
                <div class="stat-card-icon" style="background:rgba(245,158,11,0.12);color:#f59e0b;"><span class="material-symbols-outlined">business</span></div>
                <div class="stat-card-value"><span id="adminStatClients">0</span></div>
                <div class="stat-card-label">Clients</div>
              </div>
              <div class="stat-card">
                <div class="stat-card-icon" style="background:rgba(139,92,246,0.12);color:#8b5cf6;"><span class="material-symbols-outlined">home</span></div>
                <div class="stat-card-value"><span id="adminStatProps">0</span></div>
                <div class="stat-card-label">Biens</div>
              </div>
              <div class="stat-card">
                <div class="stat-card-icon" style="background:rgba(239,68,68,0.12);color:#ef4444;"><span class="material-symbols-outlined">assessment</span></div>
                <div class="stat-card-value"><span id="adminStatAssessments">0</span></div>
                <div class="stat-card-label">Evaluations</div>
              </div>
              <div class="stat-card">
                <div class="stat-card-icon" style="background:rgba(34,197,94,0.12);color:#22c55e;"><span class="material-symbols-outlined">calendar_month</span></div>
                <div class="stat-card-value"><span id="adminStatMonth">0</span></div>
                <div class="stat-card-label">Ce mois</div>
              </div>
            </div>

            <!-- Two column layout: users + activity -->
            <div class="admin-grid">
              <div class="card">
                <div class="card-header">
                  <h3 style="font-size:14px;font-weight:600;">Derniers utilisateurs</h3>
                  <button class="admin-tab-btn" id="adminTabUsers" style="background:none;border:none;font-size:11px;color:var(--color-primary);cursor:pointer;padding:0;">Voir tout</button>
                </div>
                <div class="card-body" style="padding:0;">
                  <table class="data-table">
                    <thead><tr><th>Nom</th><th>Email</th><th>Role</th></tr></thead>
                    <tbody id="adminRecentUsers"></tbody>
                  </table>
                </div>
              </div>
              <div class="card">
                <div class="card-header">
                  <h3 style="font-size:14px;font-weight:600;">Evaluations recentes</h3>
                  <button class="admin-tab-btn" id="adminTabAudit" style="background:none;border:none;font-size:11px;color:var(--color-primary);cursor:pointer;padding:0;">Voir tout</button>
                </div>
                <div class="card-body" id="adminRecentAssessments" style="font-size:12px;color:var(--text-primary);"></div>
              </div>
            </div>
          </div>

          <!-- Users full table (hidden by default) -->
          <div class="admin-users-content" style="display:none;">
            <button class="admin-back-btn" style="background:none;border:none;font-size:12px;color:var(--color-primary);cursor:pointer;display:flex;align-items:center;gap:4px;margin-bottom:16px;padding:0;">
              <span class="material-symbols-outlined" style="font-size:16px!important;">arrow_back</span> Retour au tableau de bord
            </button>
            <div class="card">
              <div class="card-body" style="padding:0;">
                <table class="data-table">
                  <thead><tr><th>Nom</th><th>Email</th><th>Role</th></tr></thead>
                  <tbody id="adminAllUsersTable"></tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Audit full table (hidden by default) -->
          <div class="admin-audit-content" style="display:none;">
            <button class="admin-back-btn" style="background:none;border:none;font-size:12px;color:var(--color-primary);cursor:pointer;display:flex;align-items:center;gap:4px;margin-bottom:16px;padding:0;">
              <span class="material-symbols-outlined" style="font-size:16px!important;">arrow_back</span> Retour au tableau de bord
            </button>
            <div class="card">
              <div class="card-body" style="padding:0;">
                <table class="data-table">
                  <thead><tr><th>Adresse</th><th>Statut</th><th>Score</th><th>Date</th></tr></thead>
                  <tbody id="adminAuditTable"></tbody>
                </table>
              </div>
            </div>
          </div>
        </section>

        <!-- ====== VIEW: Admin Settings ====== -->'''

if old_admin_panel_start in content and old_admin_panel_end in content:
    start_idx = content.find(old_admin_panel_start)
    end_idx = content.find(old_admin_panel_end)
    if start_idx >= 0 and end_idx > start_idx:
        content = content[:start_idx] + new_admin_html + content[end_idx:]
        print("[OK] Replaced admin dashboard HTML with brand-aligned components")
    else:
        print("[FAIL] Could not find admin panel boundaries")
else:
    print(f"[FAIL] Admin panel markers not found")
    print(f"  start found: {old_admin_panel_start in content}")
    print(f"  end found: {old_admin_panel_end in content}")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[DONE] HTML fixes applied")
