"""
Add Outfit Google Font + enrich empty admin/expert view panels.
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Add Outfit font ────────────────────────────────────────
old_font_block = '''    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,300,0..1,0" rel="stylesheet">'''
new_font_block = '''    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,300,0..1,0" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">'''

if old_font_block in content:
    content = content.replace(old_font_block, new_font_block)
    print("✅ Outfit font added to head")
else:
    print("⚠️ Material Symbols link not found exactly, trying flexible match")
    # Find any google fonts link and add after it
    idx = content.find('href="https://fonts.googleapis.com/css2?family=Material+Symbols')
    if idx > 0:
        end = content.find('"', idx + 30)
        insert_at = content.find('>', end) + 1
        content = content[:insert_at] + '\n    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">' + content[insert_at:]
        print("✅ Outfit font added (flexible match)")
    else:
        print("❌ Could not find Material Symbols link at all")

# ── 2. Enrich admin views ─────────────────────────────────────
admin_overview = '''        <!-- ADMIN VIEWS -->
        <section class="view-panel" id="view-admin-overview">
          <div class="admin-dashboard">
            <div class="admin-stats-row" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;padding:16px 0;">
              <div class="dashboard-card" style="padding:16px;"><span class="material-symbols-outlined" style="font-size:20px;color:#6366f1;">group</span><span class="stat-card-value" style="font-size:24px;font-weight:600;display:block;" id="adminStatUsers">0</span><span class="stat-card-label" style="font-size:11px;color:var(--text-muted);">Utilisateurs</span></div>
              <div class="dashboard-card" style="padding:16px;"><span class="material-symbols-outlined" style="font-size:20px;color:#3b82f6;">badge</span><span class="stat-card-value" style="font-size:24px;font-weight:600;display:block;" id="adminStatAssureurs">0</span><span class="stat-card-label" style="font-size:11px;color:var(--text-muted);">Assureurs</span></div>
              <div class="dashboard-card" style="padding:16px;"><span class="material-symbols-outlined" style="font-size:20px;color:#10b981;">person_pin</span><span class="stat-card-value" style="font-size:24px;font-weight:600;display:block;" id="adminStatAssures">0</span><span class="stat-card-label" style="font-size:11px;color:var(--text-muted);">Assurés</span></div>
              <div class="dashboard-card" style="padding:16px;"><span class="material-symbols-outlined" style="font-size:20px;color:#f59e0b;">business</span><span class="stat-card-value" style="font-size:24px;font-weight:600;display:block;" id="adminStatClients">0</span><span class="stat-card-label" style="font-size:11px;color:var(--text-muted);">Clients</span></div>
              <div class="dashboard-card" style="padding:16px;"><span class="material-symbols-outlined" style="font-size:20px;color:#8b5cf6;">home</span><span class="stat-card-value" style="font-size:24px;font-weight:600;display:block;" id="adminStatProps">0</span><span class="stat-card-label" style="font-size:11px;color:var(--text-muted);">Biens</span></div>
              <div class="dashboard-card" style="padding:16px;"><span class="material-symbols-outlined" style="font-size:20px;color:#ef4444;">assessment</span><span class="stat-card-value" style="font-size:24px;font-weight:600;display:block;" id="adminStatAssessments">0</span><span class="stat-card-label" style="font-size:11px;color:var(--text-muted);">Évaluations</span></div>
            </div>
            <div class="admin-section" style="display:grid;grid-template-columns:2fr 1fr;gap:16px;">
              <div class="dashboard-card" style="padding:16px;">
                <h3 style="font-size:14px;font-weight:600;margin-bottom:12px;">Activité récente</h3>
                <div id="adminActivityList" style="display:flex;flex-direction:column;gap:8px;">
                  <div class="activity-item" style="padding:8px 0;border-bottom:1px solid var(--border-color);font-size:13px;color:var(--text-secondary);">Aucune activité récente</div>
                </div>
              </div>
              <div class="dashboard-card" style="padding:16px;">
                <h3 style="font-size:14px;font-weight:600;margin-bottom:12px;">Actions rapides</h3>
                <div style="display:flex;flex-direction:column;gap:8px;">
                  <button class="risk-btn primary" style="width:100%;" onclick="alert('Créer un utilisateur — modal à implémenter')"><span class="material-symbols-outlined" style="font-size:16px;">person_add</span> Nouvel utilisateur</button>
                  <button class="risk-btn secondary" style="width:100%;" onclick="alert('Rapport système — à implémenter')"><span class="material-symbols-outlined" style="font-size:16px;">description</span> Rapport système</button>
                </div>
              </div>
            </div>
          </div>
        </section>
        <section class="view-panel" id="view-admin-clients">
          <div class="admin-clients-table" style="padding:16px 0;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
              <h3 style="font-size:16px;font-weight:600;">Gestion des utilisateurs</h3>
              <div style="display:flex;gap:8px;">
                <input type="text" id="adminClientsSearch" placeholder="Rechercher..." style="padding:8px 12px;border:1px solid var(--border-color);border-radius:8px;background:var(--bg-panel);color:var(--text-primary);font-family:var(--font-primary);font-size:13px;width:220px;">
                <button class="risk-btn primary" id="adminAddUserBtn" style="height:36px;"><span class="material-symbols-outlined" style="font-size:16px;">add</span> Ajouter</button>
              </div>
            </div>
            <div class="table-wrapper" style="overflow-x:auto;border:1px solid var(--border-color);border-radius:12px;">
              <table class="clients-table" style="width:100%;border-collapse:collapse;">
                <thead><tr style="background:var(--bg-panel);text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;color:var(--text-muted);"><th style="padding:10px 14px;">Nom</th><th style="padding:10px 14px;">Email</th><th style="padding:10px 14px;">Rôle</th><th style="padding:10px 14px;">Statut</th><th style="padding:10px 14px;">Actions</th></tr></thead>
                <tbody id="adminClientsBody">
                  <tr><td colspan="5" style="padding:24px;text-align:center;color:var(--text-muted);font-size:13px;">Chargement des utilisateurs…</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>
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

        <!-- EXPERT VIEWS -->
        <section class="view-panel" id="view-expert-missions">
          <div class="expert-missions" style="padding:16px 0;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
              <div><h3 style="font-size:16px;font-weight:600;">Missions d'inspection</h3><p style="font-size:12px;color:var(--text-muted);">Évaluations de biens qui vous sont assignées</p></div>
              <div style="display:flex;gap:8px;">
                <select id="expertMissionFilter" style="padding:8px 12px;border:1px solid var(--border-color);border-radius:8px;background:var(--bg-panel);color:var(--text-primary);font-family:var(--font-primary);font-size:13px;">
                  <option value="all">Toutes</option>
                  <option value="pending">En attente</option>
                  <option value="in_progress">En cours</option>
                  <option value="completed">Terminées</option>
                </select>
              </div>
            </div>
            <div class="missions-grid" id="expertMissionsGrid" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px;">
              <div class="dashboard-card" style="padding:20px;text-align:center;color:var(--text-muted);font-size:13px;">Aucune mission pour le moment</div>
            </div>
          </div>
        </section>
        <section class="view-panel" id="view-expert-settings">
          <div class="settings-container" style="padding:16px 0;">
            <div class="settings-tabs" id="expertSettingsTabs" style="display:flex;gap:0;border-bottom:1px solid var(--border-color);margin-bottom:20px;">
              <button class="settings-tab active" data-stab="profile">Profil</button>
              <button class="settings-tab" data-stab="preferences">Préférences</button>
            </div>
            <div class="settings-content active" data-scontent="profile">
              <div class="dashboard-card" style="padding:20px;">
                <h4 style="font-size:14px;font-weight:600;margin-bottom:16px;">Mon profil expert</h4>
                <div class="settings-field"><label style="font-size:12px;color:var(--text-secondary);display:block;margin-bottom:4px;">Spécialité</label>
                  <select class="afi-select" style="max-width:360px;">
                    <option>Inondation</option>
                    <option>Séisme</option>
                    <option>Incendie</option>
                    <option selected>Généraliste</option>
                  </select>
                </div>
                <div class="settings-field" style="margin-top:12px;"><label style="font-size:12px;color:var(--text-secondary);display:block;margin-bottom:4px;">Disponible</label>
                  <label class="switch"><input type="checkbox" checked><span class="slider round"></span></label>
                </div>
              </div>
            </div>
            <div class="settings-content" data-scontent="preferences">
              <div class="dashboard-card" style="padding:20px;">
                <h4 style="font-size:14px;font-weight:600;margin-bottom:16px;">Préférences</h4>
                <p style="font-size:13px;color:var(--text-secondary);">Paramètres de préférences — à implémenter.</p>
              </div>
            </div>
          </div>
        </section>'''

# Find the old admin/expert placeholder block
old_block = '''        <!-- ADMIN VIEWS -->
        <section class="view-panel" id="view-admin-overview"><div class="admin-layout"><h3>Admin Overview</h3></div></section>
        <section class="view-panel" id="view-admin-clients"><div class="admin-layout"><h3>Admin Clients</h3></div></section>
        <section class="view-panel" id="view-admin-settings"><div class="admin-layout"><h3>Admin Settings</h3></div></section>

        <!-- EXPERT VIEWS -->
        <section class="view-panel" id="view-expert-missions"><div class="expert-layout"><h3>Mes Missions</h3></div></section>
        <section class="view-panel" id="view-expert-settings"><div class="expert-layout"><h3>Expert Settings</h3></div></section>'''

if old_block in content:
    content = content.replace(old_block, admin_overview)
    print("✅ Admin & Expert views enriched")
else:
    print("⚠️ Exact match not found, trying regex...")
    # Use regex to match more flexibly
    pattern = r'\s*<!-- ADMIN VIEWS -->.*?</section>.*?</section>.*?</section>\s*\n\s*<!-- EXPERT VIEWS -->.*?</section>.*?</section>'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content[:match.start()] + '\n' + admin_overview + content[match.end():]
        print("✅ Admin & Expert views enriched (regex)")
    else:
        print("❌ Could not match admin/expert block at all")

# ── 3. Write back ──────────────────────────────────────────────
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ index.html updated successfully")
