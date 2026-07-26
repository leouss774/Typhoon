"""
Direct fixes for:
1. Restore missing <section class="view-panel" id="view-settings"> wrapper
2. Replace admin dashboard custom CSS with brand-aligned components (.stat-card, .card, .data-table)
"""
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix settings view - add the proper opening section tag BEFORE the ACCOUNT sub-tab
# Line 2273: <!-- ====== VIEW: Admin Settings ====== -->
# Line 2274:           <!-- ACCOUNT sub-tab - Matching reference layout -->
# After line 2273, before line 2274, insert: <section class="view-panel" id="view-settings">

old_settings = '<!-- ====== VIEW: Admin Settings ====== -->\n          <!-- ACCOUNT sub-tab'
new_settings = '<!-- ====== VIEW: Admin Settings ====== -->\n        <section class="view-panel" id="view-settings">\n          <!-- ACCOUNT sub-tab'
if old_settings in content:
    content = content.replace(old_settings, new_settings, 1)
    print("[OK] Added missing <section> wrapper for settings view")
else:
    print("[FAIL] Could not fix settings view - pattern mismatch")
    # Debug: show what's actually there
    idx = content.find('Admin Settings')
    if idx >= 0:
        snippet = content[idx:idx+150]
        print(f"  Found at pos {idx}: {repr(snippet[:100])}")

# 2. Replace the admin dashboard header and stats area with brand-aligned components
# Find the admin dashboard section
old_admin_start = '        <!-- ====== VIEW: Admin Dashboard ====== -->\n        <section class="view-panel" id="view-admin-dashboard">\n          <div class="admin-header">'
new_admin_start = '        <!-- ====== VIEW: Admin Dashboard ====== -->\n        <section class="view-panel" id="view-admin-dashboard">\n          <div class="view-header" style="display:flex;align-items:center;gap:16px;margin-bottom:24px;flex-wrap:wrap;">'
if old_admin_start in content:
    content = content.replace(old_admin_start, new_admin_start, 1)
    print("[OK] Fixed admin header class -> view-header")
else:
    print("[FAIL] Could not find admin header")

# 3. Replace admin section classes with standard .card classes
old_section = '<div class="admin-section">'
new_section = '<div class="card" style="margin-bottom:0;">'
if old_section in content:
    content = content.replace(old_section, new_section, 2)
    print("[OK] Replaced admin-section -> card")
else:
    print("[FAIL] Could not find admin-section")

# 4. Replace admin-grid with standard grid
old_grid = 'class="admin-grid"'
new_grid = 'class="card-grid two-col"'
if old_grid in content:
    content = content.replace(old_grid, new_grid, 1)
    print("[OK] Replaced admin-grid -> card-grid two-col")
else:
    print("[FAIL] Could not find admin-grid")

# 5. Replace admin-stats with kpi-grid
old_stats = 'class="admin-stats"'
new_stats = 'class="kpi-grid wide"'
if old_stats in content:
    content = content.replace(old_stats, new_stats, 1)
    print("[OK] Replaced admin-stats -> kpi-grid wide")
else:
    print("[FAIL] Could not find admin-stats")

# 6. Replace admin-stat-card with stat-card
old_stat_card = 'class="admin-stat-card"'
new_stat_card = 'class="stat-card"'
if old_stat_card in content:
    content = content.replace(old_stat_card, new_stat_card)
    print("[OK] Replaced admin-stat-card -> stat-card")
else:
    print("[FAIL] Could not find admin-stat-card")

# 7. Replace admin-stat-icon with stat-card-icon
old_icon = 'class="admin-stat-icon"'
new_icon = 'class="stat-card-icon"'
if old_icon in content:
    content = content.replace(old_icon, new_icon)
    print("[OK] Replaced admin-stat-icon -> stat-card-icon")
else:
    print("[FAIL] Could not find admin-stat-icon")

# 8. Replace admin-stat-value with stat-card-value
old_val = 'class="admin-stat-value"'
new_val = 'class="stat-card-value"'
if old_val in content:
    content = content.replace(old_val, new_val)
    print("[OK] Replaced admin-stat-value -> stat-card-value")
else:
    print("[FAIL] Could not find admin-stat-value")

# 9. Replace admin-stat-label with stat-card-label
old_label = 'class="admin-stat-label"'
new_label = 'class="stat-card-label"'
if old_label in content:
    content = content.replace(old_label, new_label)
    print("[OK] Replaced admin-stat-label -> stat-card-label")
else:
    print("[FAIL] Could not find admin-stat-label")

# 10. Replace admin-section-header with card-header
old_header = 'class="admin-section-header"'
new_header = 'class="card-header"'
if old_header in content:
    content = content.replace(old_header, new_header, 2)
    print("[OK] Replaced admin-section-header -> card-header")
else:
    print("[FAIL] Could not find admin-section-header")

# 11. Replace admin-users-table with data-table
old_table = 'class="admin-users-table"'
new_table = 'class="data-table"'
if old_table in content:
    content = content.replace(old_table, new_table)
    print("[OK] Replaced admin-users-table -> data-table")
else:
    print("[FAIL] Could not find admin-users-table")

# 12. Replace admin-activity-item with standard item
old_activity = 'class="admin-activity-item"'
new_activity = 'class="list-item"'
if old_activity in content:
    content = content.replace(old_activity, new_activity)
    print("[OK] Replaced admin-activity-item -> list-item")
else:
    print("[FAIL] Could not find admin-activity-item")

# 13. Replace admin-activity-text
old_activity_text = 'class="admin-activity-text"'
new_activity_text = 'class="list-item-text"'
if old_activity_text in content:
    content = content.replace(old_activity_text, new_activity_text)
    print("[OK] Replaced admin-activity-text -> list-item-text")
else:
    print("[FAIL] Could not find admin-activity-text")

# 14. Replace admin-activity-time
old_time = 'class="admin-activity-time"'
new_time = 'class="list-item-time"'
if old_time in content:
    content = content.replace(old_time, new_time)
    print("[OK] Replaced admin-activity-time -> list-item-time")
else:
    print("[FAIL] Could not find admin-activity-time")

# 15. Replace admin-subtitle
old_sub = 'class="admin-subtitle"'
new_sub = 'class="view-subtitle"'
if old_sub in content:
    content = content.replace(old_sub, new_sub, 1)
    print("[OK] Replaced admin-subtitle -> view-subtitle")
else:
    print("[FAIL] Could not find admin-subtitle")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n[DONE] All replacements applied")
