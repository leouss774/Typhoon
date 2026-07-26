"""
Remove all expert-related elements from index.html.
"""
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# 1. Remove expert-dashboard view panel (from "VIEW: Expert - Tableau de Bord" to the next view panel)
old_dash_view = '''        <!-- ====== VIEW: Expert - Tableau de Bord ====== -->
        <section class="view-panel" id="view-expert-dashboard">'''
# Find the end of this section (until the next "VIEW: Expert - Missions")
idx_start = content.find(old_dash_view)
idx_end = content.find('        <!-- ====== VIEW: Expert - Missions ====== -->')
if idx_start >= 0 and idx_end >= 0:
    content = content[:idx_start] + content[idx_end:]
    changes += 1
    print("[OK] Removed expert-dashboard view panel")
else:
    print("[FAIL] Could not find expert-dashboard view panel")

# 2. Remove expert missions view panel (from "VIEW: Expert - Missions" to the next view panel or end)
old_missions_view = '        <!-- ====== VIEW: Expert - Missions ====== -->\n        <section class="view-panel" id="view-missions">'
# Find the end - it's the next view panel that isn't expert
remaining = content[content.find(old_missions_view):]
# Find the next view panel after missions
next_view_marker = remaining.find('        <!-- ====== VIEW:')
if next_view_marker > 0:
    next_full = remaining.find('        <section class="view-panel"')
    if next_full > 0:
        end_missions = content.find(remaining[:next_full])
        if end_missions >= 0:
            content = content[:content.find(old_missions_view)] + content[end_missions:]
            changes += 1
            print("[OK] Removed expert missions view panel")
        else:
            print("[FAIL] Could not find end of missions view panel")
    else:
        print("[FAIL] Could not find next view panel after missions")
else:
    print("[FAIL] Could not find next view marker after missions")

# 3. Remove experts (assureur management) view panel
old_experts_view = '        <!-- ====== VIEW: Assureur - Gestion des Experts ====== -->\n        <section class="view-panel" id="view-experts">'
idx = content.find(old_experts_view)
if idx >= 0:
    # Find the next view panel
    remaining = content[idx:]
    next_marker = remaining.find('        <!-- ====== VIEW:', 100)
    if next_marker > 0:
        end_experts = content.find(remaining[:next_marker])
        if end_experts >= 0:
            content = content[:idx] + content[end_experts:]
            changes += 1
            print("[OK] Removed experts (assureur) view panel")
        else:
            print("[FAIL] Could not find end of experts view panel")
    else:
        print("[FAIL] Could not find next view marker after experts")
else:
    print("[FAIL] Could not find experts view panel")

# 4. Remove expert nav items from sidebar
old_expert_nav = '''          <!-- Expert Items -->
          <button class="nav-item nav-role-expert" data-view="expert-dashboard" aria-label="Tableau de bord" style="display:none;">
            <span class="material-symbols-outlined">dashboard</span>
            <span class="nav-label">Tableau de bord</span>
            <md-ripple></md-ripple>
          </button>
          <button class="nav-item nav-role-expert" data-view="missions" aria-label="Missions" style="display:none;">
            <span class="material-symbols-outlined">assignment</span>
            <span class="nav-label">Missions</span>
            <md-ripple></md-ripple>
          </button>
          <button class="nav-item nav-role-expert" data-view="expert-profile" aria-label="Mon Profil" style="display:none;">
            <span class="material-symbols-outlined">badge</span>
            <span class="nav-label">Mon Profil</span>
            <md-ripple></md-ripple>
          </button>

          <!-- Assur\u00e9 (Policyholder / Client) Items -->'''
new_nav = '''          <!-- Assur\u00e9 (Policyholder / Client) Items -->'''
if old_expert_nav in content:
    content = content.replace(old_expert_nav, new_nav, 1)
    changes += 1
    print("[OK] Removed expert nav items from sidebar")
else:
    print("[FAIL] Could not find expert nav items in sidebar")

# 5. Remove Experts (Assureur) nav item from sidebar
old_experts_nav = '''          <!-- Experts (Assureur) -->
          <button class="nav-item nav-role-assureur" data-view="experts" aria-label="Experts">
            <span class="material-symbols-outlined">assignment_ind</span>
            <span class="nav-label">Experts</span>
            <md-ripple></md-ripple>
          </button>
'''
if old_experts_nav in content:
    content = content.replace(old_experts_nav, '', 1)
    changes += 1
    print("[OK] Removed Experts (Assureur) nav item")
else:
    print("[FAIL] Could not find Experts (Assureur) nav item")

# 6. Remove expert invite modal and assign modal
old_invite_modal = '''        <!-- ====== MODAL: Inviter un Expert ====== -->
        <div class="modal-overlay" id="inviteExpertModal">'''
idx = content.find(old_invite_modal)
if idx >= 0:
    # Find the next modal or end
    remaining = content[idx + 100:]
    next_modal = remaining.find('modal-overlay')
    next_section = remaining.find('<!-- ======')
    end_point = min([p for p in [next_modal, next_section] if p > 0] + [len(remaining)])
    # Find the actual closing of the modal
    close_div = remaining.find('</div>')
    close_count = 0
    search_pos = 0
    while close_count < 3 and search_pos < len(remaining):
        cd = remaining.find('</div>', search_pos)
        if cd >= 0:
            close_count += 1
            search_pos = cd + 6
        else:
            break
    if search_pos > 0:
        content = content[:idx] + content[idx + search_pos:]
        changes += 1
        print("[OK] Removed invite expert modal")
    else:
        print("[FAIL] Could not find end of invite modal")
else:
    print("[FAIL] Could not find invite expert modal")

old_assign_modal = '''        <!-- ====== MODAL: Assigner un Expert ====== -->
        <div class="modal-overlay" id="assignExpertModal">'''
idx = content.find(old_assign_modal)
if idx >= 0:
    remaining = content[idx + 100:]
    close_div = remaining.find('</div>')
    close_count = 0
    search_pos = 0
    while close_count < 3 and search_pos < len(remaining):
        cd = remaining.find('</div>', search_pos)
        if cd >= 0:
            close_count += 1
            search_pos = cd + 6
        else:
            break
    if search_pos > 0:
        content = content[:idx] + content[idx + search_pos:]
        changes += 1
        print("[OK] Removed assign expert modal")
    else:
        print("[FAIL] Could not find end of assign modal")
else:
    print("[FAIL] Could not find assign expert modal")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n[OK] Total changes made: {changes}")
