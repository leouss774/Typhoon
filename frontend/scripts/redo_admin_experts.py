"""
Replace the basic view-admin-experts panel with a rich panel
that mirrors the view-clients layout (same cards, table, search styling).
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the old view-admin-experts panel boundaries
idx = content.find('id="view-admin-experts"')
if idx == -1:
    print("ERROR: view-admin-experts not found!")
    exit(1)

section_start = content.rfind('<section', 0, idx)
after = content[section_start:]
depth = 1
i = after.find('>', 50) + 1
while i < len(after) and depth > 0:
    next_open = after.find('<section', i)
    next_close = after.find('</section>', i)
    if next_close == -1:
        break
    if next_open != -1 and next_open < next_close:
        depth += 1
        i = after.find('>', next_open) + 1
    else:
        depth -= 1
        i = next_close + 10

section_end = section_start + i
old_panel = content[section_start:section_end]
print(f"Old panel: {len(old_panel)} chars")

# New rich panel matching view-clients layout
new_panel = """        <section class="view-panel" id="view-admin-experts">
          <!-- Expert Management Panel — Same layout as view-clients -->
          <div class="clients-tab-content active" data-content="info">
            <!-- Header with search + add new -->
            <div class="clients-header">
              <div>
                <h3>Experts</h3>
                <p>Gestion des experts et des missions</p>
              </div>
              <div class="clients-header-actions">
                <div class="clients-search-box">
                  <span class="material-symbols-outlined clients-search-icon">search</span>
                  <input type="text" class="clients-search-input" id="adminExpertSearch" placeholder="Rechercher un expert..." />
                </div>
                <button class="clients-add-btn" id="adminAddExpertBtn">
                  <span class="material-symbols-outlined" style="font-size:16px!important;">person_add</span>
                  Inviter un expert
                </button>
              </div>
            </div>

            <!-- Stats row -->
            <div class="clients-stats-row">
              <div class="clients-stat-card">
                <span class="clients-stat-value" id="adminExpertStatTotal">—</span>
                <span class="clients-stat-label">Total experts</span>
                <span class="clients-stat-trend positive">Gestion complète</span>
              </div>
              <div class="clients-stat-card">
                <span class="clients-stat-value" id="adminExpertStatActive">—</span>
                <span class="clients-stat-label">Actifs</span>
                <span class="clients-stat-trend positive">Disponibles</span>
              </div>
              <div class="clients-stat-card">
                <span class="clients-stat-value" id="adminExpertStatPending">—</span>
                <span class="clients-stat-label">En attente</span>
                <span class="clients-stat-trend negative">Validation requise</span>
              </div>
              <div class="clients-stat-card">
                <span class="clients-stat-value" id="adminExpertStatMissions">—</span>
                <span class="clients-stat-label">Missions actives</span>
                <span class="clients-stat-trend positive">En cours</span>
              </div>
            </div>

            <!-- Experts Data Table -->
            <div class="clients-table-wrapper">
              <table class="clients-table">
                <thead>
                  <tr>
                    <th class="col-client">Expert</th>
                    <th class="col-ref">Email</th>
                    <th class="col-type">Specialite</th>
                    <th class="col-status">Statut</th>
                    <th class="col-actions">Actions</th>
                  </tr>
                </thead>
                <tbody id="adminExpertTableBody">
                  <tr><td colspan="5" style="padding:24px;text-align:center;color:var(--text-muted);font-size:13px;">Chargement des experts...</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>"""

content = content[:section_start] + new_panel + content[section_end:]
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"New panel: {len(new_panel)} chars")
print("✅ Replaced admin-experts panel with rich version")
