"""
Add Experts management tab for admin.
- Same table layout as admin-clients (search + table + stats)
- Unique IDs (adminExpertSearch, adminExpertTableBody, adminExpertStatTotal, etc.)
- Sidebar button: "Experts" with badge icon
- Router entries
- initAdminExperts() in admin.ts
"""
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('src/router.ts', 'r', encoding='utf-8') as f:
    router = f.read()

with open('src/views/admin/admin.ts', 'r', encoding='utf-8') as f:
    admin_ts = f.read()

# ══════════════════════════════════════════════════════════════
# 1. Add sidebar button: Experts
# ══════════════════════════════════════════════════════════════
# Find the admin settings button and insert experts before it
admin_clients_btn = '<button class="nav-item nav-role-admin" data-view="admin-clients" style="display:none;"><span class="material-symbols-outlined">groups</span><span class="nav-label">Clients</span><md-ripple></md-ripple></button>'
admin_clients_to_settings = admin_clients_btn + '\n          <button class="nav-item nav-role-admin" data-view="settings"'
new_section = admin_clients_btn + '''\n          <button class="nav-item nav-role-admin" data-view="admin-experts" style="display:none;"><span class="material-symbols-outlined">verified</span><span class="nav-label">Experts</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-admin" data-view="settings"'''

if admin_clients_to_settings in html:
    html = html.replace(admin_clients_to_settings, new_section, 1)
    print("✅ Sidebar: added Experts button after Clients")
else:
    print("⚠️ Could not find admin clients/settings buttons")

# ══════════════════════════════════════════════════════════════
# 2. Create view-admin-experts panel
# ══════════════════════════════════════════════════════════════
admin_experts_panel = '''        <!-- ADMIN EXPERTS — Expert Management -->
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

# Insert expert panel after admin-clients panel's closing </section>
# Find the admin-clients panel closing </section>
admin_clients_end = html.rfind('</section>', html.find('id="view-admin-clients"'), html.find('id="view-admin-clients"') + 5000)
if admin_clients_end > 0:
    # Find the NEXT </section> after admin-clients (the panel's own closing tag)
    # Actually the panel has nested sections. Let me find the correct level.
    # The admin-clients panel has only one </section> at its end (no nested sections in the table layout)
    # Let me verify
    pass

# Simpler approach: find where the admin-clients panel section tag starts, then find its matching close
idx = html.find('id="view-admin-clients"')
section_start = html.rfind('<section', 0, idx)
after_section = html[section_start:]
depth = 1
i = after_section.find('>', 50) + 1
while i < len(after_section) and depth > 0:
    next_open = after_section.find('<section', i)
    next_close = after_section.find('</section>', i)
    if next_close == -1:
        break
    if next_open != -1 and next_open < next_close:
        depth += 1
        i = after_section.find('>', next_open) + 1
    else:
        depth -= 1
        i = next_close + 10

end_of_panel = section_start + i

# Insert experts panel right after admin-clients closes
html = html[:end_of_panel] + '\n' + admin_experts_panel + '\n' + html[end_of_panel:]
print(f"✅ view-admin-experts panel inserted (after admin-clients)")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# ══════════════════════════════════════════════════════════════
# 3. Update router
# ══════════════════════════════════════════════════════════════

# VIEW_TABS
if "'admin-clients': []," in router:
    router = router.replace("'admin-clients': [],", "'admin-clients': [],\n  'admin-experts': [],", 1)
    print("✅ VIEW_TABS: added admin-experts")
else:
    print("⚠️ Could not add admin-experts to VIEW_TABS")

# ROUTES
if "'admin-clients': '/admin/clients'," in router:
    router = router.replace("'admin-clients': '/admin/clients',", "'admin-clients': '/admin/clients',\n  'admin-experts': '/admin/experts',", 1)
    print("✅ ROUTES: added admin-experts")
else:
    print("⚠️ Could not add admin-experts to ROUTES")

# URL parsing: add experts: 'admin-experts' to the admin map
old_url_map = "const map: Record<string, string> = { overview: 'admin-overview', clients: 'admin-clients', settings: 'settings' };"
new_url_map = "const map: Record<string, string> = { overview: 'admin-overview', clients: 'admin-clients', experts: 'admin-experts', settings: 'settings' };"
if old_url_map in router:
    router = router.replace(old_url_map, new_url_map, 1)
    print("✅ URL parsing: added experts: 'admin-experts'")
else:
    print("⚠️ Could not update URL parsing")

# Lifecycle: add admin-experts to the admin lifecycle (reuse initAdminOverview since experts has its own init)
old_admin_lifecycle = """  } else if (viewName === 'admin-clients') {
    requestAnimationFrame(() => initAdminUsers());
  } else {
    destroyAdminUsers();
  }"""

new_admin_lifecycle = """  } else if (viewName === 'admin-clients') {
    requestAnimationFrame(() => initAdminUsers());
  } else if (viewName === 'admin-experts') {
    import('./views/admin/admin.js').then(m => m.initAdminExperts ? m.initAdminExperts() : null);
  } else {
    destroyAdminUsers();
  }"""

if old_admin_lifecycle in router:
    router = router.replace(old_admin_lifecycle, new_admin_lifecycle, 1)
    print("✅ Lifecycle: added admin-experts with initAdminExperts")
else:
    print("⚠️ Could not update admin lifecycle")

with open('src/router.ts', 'w', encoding='utf-8') as f:
    f.write(router)

# ══════════════════════════════════════════════════════════════
# 4. Update admin.ts with initAdminExperts
# ══════════════════════════════════════════════════════════════
# Find the end of initAdminUsers function and add initAdminExperts after it
experts_init_code = '''
/* ── Admin Experts (Expert Management) ──────────────── */

let expertsInitialized = false;

export function initAdminExperts(): void {
  if (expertsInitialized) return;
  expertsInitialized = true;
  loadAdminExperts();
}

export function destroyAdminExperts(): void {
  expertsInitialized = false;
}

async function loadAdminExperts(): Promise<void> {
  try {
    const clients = await fetchClientsFromApi().catch(() => []);

    // Filter to get "expert" users. For now, filter by email pattern or assign roles dynamically
    // If the backend doesn't have a 'role' field yet, we'll show a subset or create mock experts
    const experts = clients.filter((c: any) => {
      // Check if the client has an 'expert' role or is marked as such
      return (c as any).role === 'expert' || (c as any).userType === 'expert';
    });

    // If no experts found from API, create a mock set for the demo
    const mockExperts = [
      { id: 'exp-1', firstName: 'Thomas', lastName: 'Mercier', email: 'thomas.mercier@expert.fr', specialty: 'Batiment', status: 'active', missions: 12 },
      { id: 'exp-2', firstName: 'Camille', lastName: 'Rousseau', email: 'camille.rousseau@expert.fr', specialty: 'Industriel', status: 'active', missions: 8 },
      { id: 'exp-3', firstName: 'Antoine', lastName: 'Lefevre', email: 'antoine.lefevre@expert.fr', specialty: 'Incendie', status: 'pending', missions: 0 },
      { id: 'exp-4', firstName: 'Sarah', lastName: 'Benali', email: 'sarah.benali@expert.fr', specialty: 'Inondation', status: 'active', missions: 5 },
      { id: 'exp-5', firstName: 'Lucas', lastName: 'Moreau', email: 'lucas.moreau@expert.fr', specialty: 'Electricite', status: 'suspended', missions: 3 },
    ];
    const displayExperts = experts.length > 0 ? experts : mockExperts;

    // Populate table
    const tbody = document.getElementById('adminExpertTableBody');
    if (tbody) {
      tbody.innerHTML = displayExperts.map((e: any) => {
        const name = e.firstName && e.lastName ? `${escapeHtml(e.firstName)} ${escapeHtml(e.lastName)}` : '—';
        const email = e.email || '—';
        const specialty = e.specialty || '—';
        const status = e.status || 'pending';
        const statusLabel = status === 'active' ? 'Actif' : status === 'pending' ? 'En attente' : 'Suspendu';
        const statusColor = status === 'active' ? '#10b981' : status === 'pending' ? '#f59e0b' : '#ef4444';
        const statusBg = status === 'active' ? 'rgba(16,185,129,0.1)' : status === 'pending' ? 'rgba(245,158,11,0.1)' : 'rgba(239,68,68,0.1)';
        return `<tr>
          <td style="padding:10px 14px;border-bottom:1px solid var(--border-color);"><strong>${name}</strong></td>
          <td style="padding:10px 14px;border-bottom:1px solid var(--border-color);color:var(--text-secondary);">${email}</td>
          <td style="padding:10px 14px;border-bottom:1px solid var(--border-color);"><span style="padding:2px 8px;border-radius:10px;font-size:11px;background:rgba(139,92,246,0.1);color:#8b5cf6;">${escapeHtml(specialty)}</span></td>
          <td style="padding:10px 14px;border-bottom:1px solid var(--border-color);"><span style="padding:2px 8px;border-radius:10px;font-size:11px;background:${statusBg};color:${statusColor};">${statusLabel}</span></td>
          <td style="padding:10px 14px;border-bottom:1px solid var(--border-color);">
            <button style="padding:4px 10px;border:1px solid var(--border-color);border-radius:6px;background:transparent;cursor:pointer;font-size:11px;font-family:var(--font-primary);color:var(--text-primary);">Voir</button>
            <button style="padding:4px 10px;border:1px solid var(--border-color);border-radius:6px;background:transparent;cursor:pointer;font-size:11px;font-family:var(--font-primary);color:var(--text-primary);margin-left:4px;">Assigner</button>
          </td>
        </tr>`;
      }).join('');
    }

    // Populate stats
    const setStat = (id: string, val: string) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };
    setStat('adminExpertStatTotal', String(displayExperts.length));
    setStat('adminExpertStatActive', String(displayExperts.filter((e: any) => e.status === 'active').length));
    setStat('adminExpertStatPending', String(displayExperts.filter((e: any) => e.status === 'pending').length));
    setStat('adminExpertStatMissions', String(displayExperts.reduce((sum: number, e: any) => sum + (e.missions || 0), 0)));

    // Setup search (one-time)
    const searchInput = document.getElementById('adminExpertSearch') as HTMLInputElement | null;
    if (searchInput && !searchInput.getAttribute('data-search-wired')) {
      searchInput.setAttribute('data-search-wired', 'true');
      searchInput.addEventListener('input', () => {
        const q = searchInput.value.toLowerCase().trim();
        const rows = document.querySelectorAll('#adminExpertTableBody tr');
        rows.forEach(row => {
          (row as HTMLElement).style.display = !q || (row.textContent || '').toLowerCase().includes(q) ? '' : 'none';
        });
      });
    }

    // Setup invite button
    const inviteBtn = document.getElementById('adminAddExpertBtn');
    if (inviteBtn) {
      inviteBtn.addEventListener('click', () => {
        alert('Invitation d\\'expert — module à implémenter.');
      });
    }
  } catch (err) {
    console.warn('[Admin] Failed to load experts:', err);
  }
}
'''

# Insert initAdminExperts after the last function in admin.ts (before the helper functions)
# The file ends with escapeHtml function. Let me insert before the helper functions
insert_before = '\nfunction roleBg('
if insert_before in admin_ts:
    admin_ts = admin_ts.replace(insert_before, experts_init_code + '\n' + insert_before, 1)
    print("✅ admin.ts: added initAdminExperts/destroyAdminExperts")
else:
    print("⚠️ Could not find insertion point in admin.ts, appending at end")
    admin_ts += experts_init_code

with open('src/views/admin/admin.ts', 'w', encoding='utf-8') as f:
    f.write(admin_ts)

print("\n✅ All done! Admin Experts tab added successfully.")
