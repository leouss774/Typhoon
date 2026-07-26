"""
Align IDs between view-admin-users and admin.ts initAdminUsers().
adminUsersBody → adminUserTableBody
adminUsersSearch → adminUserSearch
"""
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# In view-admin-users, replace adminUsersBody → adminUserTableBody
if 'adminUsersBody' in content:
    content = content.replace('adminUsersBody', 'adminUserTableBody', 1)
    print("✅ adminUsersBody → adminUserTableBody")
    changes += 1

if 'adminUsersSearch' in content:
    content = content.replace('adminUsersSearch', 'adminUserSearch', 1)
    print("✅ adminUsersSearch → adminUserSearch")
    changes += 1

if changes > 0:
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ {changes} changes applied")
else:
    print("⚠️ No changes needed")

# Also fix the event listener accumulation in admin.ts
with open('src/views/admin/admin.ts', 'r', encoding='utf-8') as f:
    admin_ts = f.read()

# Replace the search setup inside loadAdminUsers with a one-time setup
old_search = '''    // Setup search
    const searchInput = document.getElementById('adminUserSearch') as HTMLInputElement | null;
    if (searchInput && tbody) {
      searchInput.addEventListener('input', () => {
        const q = searchInput.value.toLowerCase().trim();
        tbody.querySelectorAll('tr').forEach(row => {
          (row as HTMLElement).style.display = !q || (row.textContent || '').toLowerCase().includes(q) ? '' : 'none';
        });
      });
    }'''

new_search = '''  // Setup search (one-time)
  const searchInput = document.getElementById('adminUserSearch') as HTMLInputElement | null;
  const tableBody = document.getElementById('adminUserTableBody');
  if (searchInput && !searchInput.getAttribute('data-search-wired')) {
    searchInput.setAttribute('data-search-wired', 'true');
    searchInput.addEventListener('input', () => {
      const q = searchInput.value.toLowerCase().trim();
      const rows = document.querySelectorAll('#adminUserTableBody tr, #adminUserTableBody tr');
      rows.forEach(row => {
        (row as HTMLElement).style.display = !q || (row.textContent || '').toLowerCase().includes(q) ? '' : 'none';
      });
    });
  }'''

if old_search in admin_ts:
    admin_ts = admin_ts.replace(old_search, new_search, 1)
    with open('src/views/admin/admin.ts', 'w', encoding='utf-8') as f:
        f.write(admin_ts)
    print("✅ Search event listener moved to one-time setup (no accumulation)")
else:
    print("⚠️ Could not find old search setup in admin.ts")

print("\n✅ Done!")
