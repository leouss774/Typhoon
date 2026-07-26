"""
Add to index.html:
1. Stat cards row (after banner-section, before widgets-grid)
2. Pending submissions section + activity timeline (before widgets-grid)
3. Notification badge in sidebar (near Clients button)
"""

import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Stat cards row ──
stat_cards_html = """
          <!-- Stat cards row (populated by overview.ts from API) -->
          <section class="dashboard-stats-row" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;padding:16px 0 8px;">
            <div class="dashboard-card" style="padding:16px;display:flex;flex-direction:column;gap:4px;">
              <span class="material-symbols-outlined" style="font-size:20px;color:var(--color-primary);">group</span>
              <span class="stat-card-value" style="font-size:24px;font-weight:600;color:var(--text-primary);" id="statTotalClients">—</span>
              <span class="stat-card-label" style="font-size:11px;color:var(--text-muted);">Clients</span>
            </div>
            <div class="dashboard-card" style="padding:16px;display:flex;flex-direction:column;gap:4px;">
              <span class="material-symbols-outlined" style="font-size:20px;color:#10b981;">check_circle</span>
              <span class="stat-card-value" style="font-size:24px;font-weight:600;color:var(--text-primary);" id="statActiveClients">—</span>
              <span class="stat-card-label" style="font-size:11px;color:var(--text-muted);">Actifs</span>
            </div>
            <div class="dashboard-card" style="padding:16px;display:flex;flex-direction:column;gap:4px;">
              <span class="material-symbols-outlined" style="font-size:20px;color:#f59e0b;">pending</span>
              <span class="stat-card-value" style="font-size:24px;font-weight:600;color:var(--text-primary);" id="statPendingClients">—</span>
              <span class="stat-card-label" style="font-size:11px;color:var(--text-muted);">En attente</span>
            </div>
            <div class="dashboard-card" style="padding:16px;display:flex;flex-direction:column;gap:4px;">
              <span class="material-symbols-outlined" style="font-size:20px;color:#6366f1;">home</span>
              <span class="stat-card-value" style="font-size:24px;font-weight:600;color:var(--text-primary);" id="statTotalProperties">—</span>
              <span class="stat-card-label" style="font-size:11px;color:var(--text-muted);">Biens</span>
            </div>
            <div class="dashboard-card" style="padding:16px;display:flex;flex-direction:column;gap:4px;">
              <span class="material-symbols-outlined" style="font-size:20px;color:#ef4444;">assessment</span>
              <span class="stat-card-value" style="font-size:24px;font-weight:600;color:var(--text-primary);" id="statTotalAssessments">—</span>
              <span class="stat-card-label" style="font-size:11px;color:var(--text-muted);">Évaluations</span>
            </div>
            <div class="dashboard-card" style="padding:16px;display:flex;flex-direction:column;gap:4px;">
              <span class="material-symbols-outlined" style="font-size:20px;color:#8b5cf6;">speed</span>
              <span class="stat-card-value" style="font-size:24px;font-weight:600;color:var(--text-primary);" id="statAvgScore">—</span>
              <span class="stat-card-label" style="font-size:11px;color:var(--text-muted);">Score moyen</span>
            </div>
            <div class="dashboard-card" style="padding:16px;display:flex;flex-direction:column;gap:4px;border:1.5px solid rgba(245,158,11,0.3);background:rgba(245,158,11,0.04);">
              <span class="material-symbols-outlined" style="font-size:20px;color:#f59e0b;">inbox</span>
              <span class="stat-card-value" style="font-size:24px;font-weight:600;color:var(--text-primary);" id="statPendingSubmissions">—</span>
              <span class="stat-card-label" style="font-size:11px;color:var(--text-muted);">Soumissions ⚠️</span>
            </div>
          </section>
"""

# Insert stat cards right after banner-section closing and before widgets-grid
old_banner_end = '          </section>\n\n          <!-- Dashboard Widgets Grid -->'
new_section = stat_cards_html + '\n          <!-- Dashboard Widgets Grid -->'
content = content.replace(old_banner_end, stat_cards_html + '          <!-- Dashboard Widgets Grid -->')

# ── 2. Activity Timeline (insert after stat cards, before the grid columns) ──
timeline_html = """          <!-- Recent Activity Timeline -->
          <section class="activity-section" style="padding:0 0 8px;">
            <div class="dashboard-card" style="padding:16px;">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                <h3 style="font-size:14px;font-weight:500;color:var(--text-primary);display:flex;align-items:center;gap:8px;">
                  <span class="material-symbols-outlined" style="font-size:18px;color:var(--color-primary);">timeline</span>
                  Activité récente
                </h3>
                <span id="activityBadge" style="font-size:11px;color:var(--text-muted);background:var(--bg-panel);padding:2px 8px;border-radius:12px;">Aujourd'hui</span>
              </div>
              <div class="activity-list" id="activityList" style="display:flex;flex-direction:column;gap:0;">
                <div id="activityPlaceholder" style="padding:16px 0;text-align:center;font-size:12px;color:var(--text-muted);">
                  <span class="material-symbols-outlined" style="font-size:32px;opacity:0.2;display:block;margin-bottom:8px;">history</span>
                  Aucune activité récente
                </div>
              </div>
            </div>
          </section>
"""

# Insert timeline after the stat cards section (before the closing div/before widgets-grid)
# Find the widgets-grid opening and insert timeline before it
old_widget_grid = '          <section class="widgets-grid">'
content = content.replace(old_widget_grid, timeline_html + '          <section class="widgets-grid">')

# ── 3. Sidebar notification badge (near Clients button) ──
# Find the Clients nav button and add a badge span
old_clients_btn = '<button class="nav-item nav-role-assureur" data-view="clients" aria-label="Clients">\n            <span class="material-symbols-outlined">groups</span>\n            <span class="nav-label">Clients</span>\n            <md-ripple></md-ripple>\n          </button>'

new_clients_btn = '<button class="nav-item nav-role-assureur" data-view="clients" aria-label="Clients">\n            <span class="material-symbols-outlined">groups</span>\n            <span class="nav-label">Clients</span>\n            <span class="nav-notification-badge" id="clientNotificationBadge" style="display:none;margin-left:auto;background:#ef4444;color:#fff;font-size:10px;font-weight:600;min-width:18px;height:18px;border-radius:9px;align-items:center;justify-content:center;padding:0 5px;">0</span>\n            <md-ripple></md-ripple>\n          </button>'

content = content.replace(old_clients_btn, new_clients_btn)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ index.html updated: stat cards + timeline + badge")
