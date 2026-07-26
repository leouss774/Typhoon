"""
Duplicate view-clients as view-admin-clients so admin has its own separate
but structurally identical clients view.
"""
import re, os

CURRENT = 'index.html'

with open(CURRENT, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ── 1. Find view-clients section ──
start = None
for i, line in enumerate(lines):
    if 'id="view-clients"' in line and 'class="view-panel"' in line:
        start = i
        break

if start is None:
    print("❌ view-clients not found")
    exit(1)

# Find end (next view-panel)
end = len(lines)
for j in range(start+1, len(lines)):
    if 'class="view-panel"' in lines[j]:
        end = j
        break

clients_html = ''.join(lines[start:end])
print(f"view-clients: lines {start+1}-{end} ({len(clients_html)} chars)")

# ── 2. Create view-admin-clients by copying view-clients ──
admin_clients_html = clients_html.replace(
    'id="view-clients"',
    'id="view-admin-clients"'
)

admin_clients_html = '        <!-- ADMIN CLIENTS (separate copy) -->\n' + admin_clients_html

# ── 3. Insert view-admin-clients after view-clients ──
# Insert after the view-clients closing </section>
insert_point = end
new_lines = lines[:insert_point] + [admin_clients_html] + lines[insert_point:]
print(f"Inserted view-admin-clients after line {insert_point}")

# ── 4. Change admin sidebar button ──
content = ''.join(new_lines)

old_sidebar = 'data-view="clients" style="display:none;"><span class="material-symbols-outlined">groups</span><span class="nav-label">Clients</span><md-ripple></md-ripple></button>'

# Find the admin one specifically (not expert)
# We need to find the one after admin-users button
admin_clients_btn = 'data-view="admin-users" style="display:none;"><span class="material-symbols-outlined">manage_accounts</span><span class="nav-label">Utilisateurs</span><md-ripple></md-ripple></button>\n          <button class="nav-item nav-role-admin" data-view="clients" style="display:none;">'
new_admin_btn = admin_clients_btn.replace('data-view="clients"', 'data-view="admin-clients"')

if admin_clients_btn in content:
    content = content.replace(admin_clients_btn, new_admin_btn, 1)
    print("✅ Admin sidebar 'Clients' → 'admin-clients'")
else:
    print("⚠️ Could not find admin clients button")
    # Try direct approach
    old_direct = 'nav-role-admin" data-view="clients" style="display:none;">'
    new_direct = 'nav-role-admin" data-view="admin-clients" style="display:none;">'
    content = content.replace(old_direct, new_direct, 1)
    print("✅ Changed via direct replacement")

# Also update /expert/clients URL parsing in router - keep expert using shared clients
# The expert sidebar still has data-view="clients" which goes to shared view
# This is fine - user only asked about admin

# ── 5. Write back ──
with open(CURRENT, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Done! File: {len(content)} chars")
