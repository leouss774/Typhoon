"""
Restore the full view-clients from original including the clientsDetailPanel.
Also add admin users management view and expert clients list view to sidebar + HTML.
"""
import re, os

CURRENT = 'index.html'
ORIGINAL_PATH = None
for p in ['/c/tmp/insurance_original/packages/front/index.html',
          'C:/tmp/insurance_original/packages/front/index.html',
          '/tmp/insurance_original/packages/front/index.html']:
    if os.path.exists(p):
        ORIGINAL_PATH = p
        break

if not ORIGINAL_PATH:
    print("Original file not found!")
    exit(1)

print(f"Original: {ORIGINAL_PATH}")

# Read both files as lines
with open(ORIGINAL_PATH, 'r', encoding='utf-8') as f:
    orig_lines = f.readlines()

with open(CURRENT, 'r', encoding='utf-8') as f:
    current = f.read()

# ── Extract full view-clients from original using line numbers ──
# Original: view-clients at line 1016, view-settings at line 1559
# So view-clients goes from line 1016 to 1558 (inclusive)
view_start = None
view_end = None
for i, line in enumerate(orig_lines):
    if 'id="view-clients"' in line and 'class="view-panel"' in line:
        view_start = i
    if view_start and i > view_start and 'id="view-settings"' in line and 'class="view-panel"' in line:
        view_end = i
        break

if view_start and view_end:
    full_orig_view = ''.join(orig_lines[view_start:view_end])
    print(f"Full original view-clients: lines {view_start+1}-{view_end} ({len(full_orig_view)} chars)")
    print(f"  Contains clientsDetailPanel: {'clientsDetailPanel' in full_orig_view}")
else:
    print(f"view_start={view_start}, view_end={view_end}")
    exit(1)

# ── Extract current view-clients and replace ──
# Find current view-clients
curr_start = None
curr_end = None
curr_lines = current.splitlines(True)
for i, line in enumerate(curr_lines):
    if 'id="view-clients"' in line and 'class="view-panel"' in line:
        curr_start = i
    if curr_start and i > curr_start and 'id="view-' in line and i > curr_start + 5:
        # Check if this starts a new view panel
        if 'class="view-panel"' in line:
            curr_end = i
            break

if curr_start and curr_end:
    curr_view = ''.join(curr_lines[curr_start:curr_end])
    print(f"\nCurrent view-clients: lines {curr_start+1}-{curr_end} ({len(curr_view)} chars)")
    
    if 'clientsDetailPanel' not in curr_view:
        # Replace the current view with the full original
        current = current.replace(curr_view, full_orig_view, 1)
        print("✅ view-clients replaced with full original (including detail panel)")
    else:
        print("✅ view-clients already has detail panel")
else:
    print(f"Could not find current view-clients")
    exit(1)

# ── Add admin users view and expert clients view ──
admin_users_view = '''
        <!-- ADMIN USER MANAGEMENT -->
        <section class="view-panel" id="view-admin-users">
          <div class="admin-users-layout" style="padding:16px 0;">
            <div class="admin-clients-table">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
                <div>
                  <h3 style="font-size:16px;font-weight:600;margin:0;">Gestion des utilisateurs</h3>
                  <p style="font-size:12px;color:var(--text-muted);margin:2px 0 0;">Tous les comptes de la plateforme</p>
                </div>
                <div style="display:flex;gap:8px;">
                  <input type="text" id="adminUsersSearch" placeholder="Rechercher..." 
                    style="padding:8px 12px;border:1px solid var(--border-color);border-radius:8px;background:var(--bg-panel);color:var(--text-primary);font-family:var(--font-primary);font-size:13px;width:220px;">
                  <button class="risk-btn primary" id="adminAddUserBtn" style="height:36px;">
                    <span class="material-symbols-outlined" style="font-size:16px;">add</span> Ajouter
                  </button>
                </div>
              </div>
              <div class="table-wrapper" style="overflow-x:auto;border:1px solid var(--border-color);border-radius:12px;">
                <table class="clients-table" style="width:100%;border-collapse:collapse;">
                  <thead>
                    <tr style="background:var(--bg-panel);text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;color:var(--text-muted);">
                      <th style="padding:10px 14px;">Utilisateur</th>
                      <th style="padding:10px 14px;">Email</th>
                      <th style="padding:10px 14px;">Rôle</th>
                      <th style="padding:10px 14px;">Statut</th>
                      <th style="padding:10px 14px;">Actions</th>
                    </tr>
                  </thead>
                  <tbody id="adminUsersBody">
                    <tr><td colspan="5" style="padding:24px;text-align:center;color:var(--text-muted);font-size:13px;">Chargement des utilisateurs…</td></tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </section>

        <!-- EXPERT CLIENTS LIST -->
        <section class="view-panel" id="view-expert-clients">
          <div class="expert-clients-layout" style="padding:16px 0;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
              <div>
                <h3 style="font-size:16px;font-weight:600;margin:0;">Biens assignés</h3>
                <p style="font-size:12px;color:var(--text-muted);margin:2px 0 0;">Propriétés à inspecter</p>
              </div>
              <div style="display:flex;gap:8px;">
                <select id="expertClientFilter" 
                  style="padding:8px 12px;border:1px solid var(--border-color);border-radius:8px;background:var(--bg-panel);color:var(--text-primary);font-family:var(--font-primary);font-size:13px;">
                  <option value="all">Tous</option>
                  <option value="pending">En attente</option>
                  <option value="in_progress">En cours</option>
                  <option value="completed">Inspecté</option>
                </select>
              </div>
            </div>
            <div class="dashboard-card" style="padding:20px;text-align:center;color:var(--text-muted);font-size:13px;">Aucun bien assigné pour le moment</div>
          </div>
        </section>
'''

# Insert after the last view-panel (before </main>)
insert_target = '</main>'
insert_before = admin_users_view + '\n      </main>'
if insert_target in current:
    current = current.replace('</main>', insert_before, 1)
    print("✅ Admin users and expert clients views added")
else:
    print("❌ Could not find </main>")

# ── Add sidebar buttons for admin-users and expert-clients ──
# Add admin-users button after admin-overview
old_admin_overview = 'data-view="admin-overview" style="display:none;"><span class="material-symbols-outlined">admin_panel_settings</span><span class="nav-label">Dashboard</span><md-ripple></md-ripple></button>'
new_admin_block = old_admin_overview + '\n          <button class="nav-item nav-role-admin" data-view="admin-users" style="display:none;"><span class="material-symbols-outlined">manage_accounts</span><span class="nav-label">Utilisateurs</span><md-ripple></md-ripple></button>'
if old_admin_overview in current:
    current = current.replace(old_admin_overview, new_admin_block, 1)
    print("✅ Added admin-users sidebar button")
else:
    print("⚠️ Could not find admin-overview button")

# Add expert-clients button after expert-missions
old_expert_missions = 'data-view="expert-missions" style="display:none;"><span class="material-symbols-outlined">assignment</span><span class="nav-label">Missions</span><md-ripple></md-ripple></button>'
new_expert_block = old_expert_missions + '\n          <button class="nav-item nav-role-expert" data-view="expert-clients" style="display:none;"><span class="material-symbols-outlined">home_work</span><span class="nav-label">Biens</span><md-ripple></md-ripple></button>'
if old_expert_missions in current:
    current = current.replace(old_expert_missions, new_expert_block, 1)
    print("✅ Added expert-clients sidebar button")
else:
    print("⚠️ Could not find expert-missions button")

# Write
with open(CURRENT, 'w', encoding='utf-8') as f:
    f.write(current)

print(f"\n✅ Done! File: {len(current)} chars")
