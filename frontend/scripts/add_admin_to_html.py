"""
Add admin sidebar nav items and view panels to index.html.
"""
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# 1. Add admin nav items after expert items in sidebar
# Find the expert items section and add admin items after it
old_after_expert = '          </button>\n\n          <!-- Assur\u00e9 (Policyholder / Client) Items -->'
admin_nav = '''          </button>

          <!-- Admin Items -->
          <button class="nav-item nav-role-admin" data-view="admin-dashboard" aria-label="Administration" style="display:none;">
            <span class="material-symbols-outlined">admin_panel_settings</span>
            <span class="nav-label">Administration</span>
            <md-ripple></md-ripple>
          </button>
          <button class="nav-item nav-role-admin" data-view="admin-users" aria-label="Utilisateurs" style="display:none;">
            <span class="material-symbols-outlined">manage_accounts</span>
            <span class="nav-label">Utilisateurs</span>
            <md-ripple></md-ripple>
          </button>
          <button class="nav-item nav-role-admin" data-view="admin-audit" aria-label="Audit" style="display:none;">
            <span class="material-symbols-outlined">summarize</span>
            <span class="nav-label">Audit</span>
            <md-ripple></md-ripple>
          </button>

          <!-- Assur\u00e9 (Policyholder / Client) Items -->'''

if old_after_expert in content:
    content = content.replace(old_after_expert, admin_nav, 1)
    changes += 1
    print("[OK] Added admin nav items to sidebar")
else:
    print("[FAIL] Could not find insertion point for admin nav")

# 2. Add admin view panels before the settings view (or after the last expert view)
# Find the settings view panel as a marker
old_settings_view = '        <!-- ====== VIEW: Admin Settings ====== -->\n        <section class="view-panel" id="view-settings">'
if old_settings_view not in content:
    old_settings_view = '        <section class="view-panel" id="view-settings">'

admin_views = '''        <!-- ====== VIEW: Admin Dashboard ====== -->
        <section class="view-panel" id="view-admin-dashboard">
          <div class="admin-header">
            <div>
              <h2><span class="material-symbols-outlined" style="font-size:24px!important;vertical-align:middle;margin-right:8px;color:var(--color-primary);">admin_panel_settings</span> Administration</h2>
              <p class="admin-subtitle">Vue d\\'ensemble de la plateforme</p>
            </div>
          </div>

          <div class="admin-dash-content">
            <!-- Stats -->
            <div class="admin-stats">
              <div class="admin-stat-card">
                <div class="admin-stat-icon" style="background:rgba(99,102,241,0.12);color:#6366f1;"><span class="material-symbols-outlined">group</span></div>
                <div><span class="admin-stat-value" id="adminStatUsers">0</span><span class="admin-stat-label">Utilisateurs</span></div>
              </div>
              <div class="admin-stat-card">
                <div class="admin-stat-icon" style="background:rgba(59,130,246,0.12);color:#3b82f6;"><span class="material-symbols-outlined">badge</span></div>
                <div><span class="admin-stat-value" id="adminStatAssureurs">0</span><span class="admin-stat-label">Assureurs</span></div>
              </div>
              <div class="admin-stat-card">
                <div class="admin-stat-icon" style="background:rgba(16,185,129,0.12);color:#10b981;"><span class="material-symbols-outlined">person_pin</span></div>
                <div><span class="admin-stat-value" id="adminStatAssures">0</span><span class="admin-stat-label">Assures</span></div>
              </div>
              <div class="admin-stat-card">
                <div class="admin-stat-icon" style="background:rgba(245,158,11,0.12);color:#f59e0b;"><span class="material-symbols-outlined">business</span></div>
                <div><span class="admin-stat-value" id="adminStatClients">0</span><span class="admin-stat-label">Clients</span></div>
              </div>
              <div class="admin-stat-card">
                <div class="admin-stat-icon" style="background:rgba(139,92,246,0.12);color:#8b5cf6;"><span class="material-symbols-outlined">home</span></div>
                <div><span class="admin-stat-value" id="adminStatProps">0</span><span class="admin-stat-label">Biens</span></div>
              </div>
              <div class="admin-stat-card">
                <div class="admin-stat-icon" style="background:rgba(239,68,68,0.12);color:#ef4444;"><span class="material-symbols-outlined">assessment</span></div>
                <div><span class="admin-stat-value" id="adminStatAssessments">0</span><span class="admin-stat-label">Evaluations</span></div>
              </div>
              <div class="admin-stat-card">
                <div class="admin-stat-icon" style="background:rgba(34,197,94,0.12);color:#22c55e;"><span class="material-symbols-outlined">calendar_month</span></div>
                <div><span class="admin-stat-value" id="adminStatMonth">0</span><span class="admin-stat-label">Ce mois</span></div>
              </div>
            </div>

            <!-- Two column: users + activity -->
            <div class="admin-grid">
              <div class="admin-section">
                <div class="admin-section-header">
                  <h3>Derniers utilisateurs</h3>
                  <button class="admin-tab-btn" id="adminTabUsers" style="background:none;border:none;font-size:11px;color:var(--color-primary);cursor:pointer;">Voir tout</button>
                </div>
                <table class="admin-users-table">
                  <thead><tr><th>Nom</th><th>Email</th><th>Role</th></tr></thead>
                  <tbody id="adminRecentUsers"></tbody>
                </table>
              </div>
              <div class="admin-section">
                <div class="admin-section-header">
                  <h3>Evaluations recentes</h3>
                  <button class="admin-tab-btn" id="adminTabAudit" style="background:none;border:none;font-size:11px;color:var(--color-primary);cursor:pointer;">Voir tout</button>
                </div>
                <div id="adminRecentAssessments"></div>
              </div>
            </div>
          </div>

          <!-- Users full table (hidden by default) -->
          <div class="admin-users-content" style="display:none;">
            <button class="admin-back-btn" id="adminBackToDash" style="background:none;border:none;font-size:12px;color:var(--color-primary);cursor:pointer;display:flex;align-items:center;gap:4px;margin-bottom:16px;">
              <span class="material-symbols-outlined" style="font-size:16px!important;">arrow_back</span> Retour au tableau de bord
            </button>
            <table class="admin-users-table">
              <thead><tr><th>Nom</th><th>Email</th><th>Role</th></tr></thead>
              <tbody id="adminAllUsersTable"></tbody>
            </table>
          </div>

          <!-- Audit full table (hidden by default) -->
          <div class="admin-audit-content" style="display:none;">
            <button class="admin-back-btn" style="background:none;border:none;font-size:12px;color:var(--color-primary);cursor:pointer;display:flex;align-items:center;gap:4px;margin-bottom:16px;">
              <span class="material-symbols-outlined" style="font-size:16px!important;">arrow_back</span> Retour au tableau de bord
            </button>
            <table class="admin-users-table">
              <thead><tr><th>Adresse</th><th>Statut</th><th>Score</th><th>Date</th></tr></thead>
              <tbody id="adminAuditTable"></tbody>
            </table>
          </div>
        </section>

        <!-- ====== VIEW: Admin Users ====== -->
        <section class="view-panel" id="view-admin-users">
          <p>Gestion des utilisateurs</p>
        </section>

        <!-- ====== VIEW: Admin Audit ====== -->
        <section class="view-panel" id="view-admin-audit">
          <p>Audit des evaluations</p>
        </section>

        <!-- ====== VIEW: Admin Settings ====== -->'''

# Insert admin views before the settings view
if old_settings_view in content:
    content = content.replace(old_settings_view, admin_views, 1)
    changes += 1
    print("[OK] Added admin view panels")
else:
    print("[FAIL] Could not find settings view panel")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n[OK] Total changes: {changes}")
