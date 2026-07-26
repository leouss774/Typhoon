"""
Revert the changes made by add_overview_features.py:
1. Remove the stat cards row (dashboard-stats-row section)
2. Remove the activity timeline section
3. Revert the sidebar badge (remove the notification badge from Clients button)
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove stat cards row (from <!-- Stat cards row --> to closing </section>)
import re
content = re.sub(
    r'\s*<!-- Stat cards row.*?</section>\n',
    '\n',
    content,
    flags=re.DOTALL
)

# 2. Remove activity timeline section
content = re.sub(
    r'\s*<!-- Recent Activity Timeline -->.*?</section>\n\s*</div>\s*\n\s*</section>\n',
    '\n',
    content,
    flags=re.DOTALL
)

# 3. Revert sidebar badge: replace the Clients button with badge back to original
old_clients_btn = '<button class="nav-item nav-role-assureur" data-view="clients" aria-label="Clients">\n            <span class="material-symbols-outlined">groups</span>\n            <span class="nav-label">Clients</span>\n            <span class="nav-notification-badge" id="clientNotificationBadge" style="display:none;margin-left:auto;background:#ef4444;color:#fff;font-size:10px;font-weight:600;min-width:18px;height:18px;border-radius:9px;align-items:center;justify-content:center;padding:0 5px;">0</span>\n            <md-ripple></md-ripple>\n          </button>'

new_clients_btn = '<button class="nav-item nav-role-assureur" data-view="clients" aria-label="Clients">\n            <span class="material-symbols-outlined">groups</span>\n            <span class="nav-label">Clients</span>\n            <md-ripple></md-ripple>\n          </button>'

# Only replace if the old pattern exists
if old_clients_btn in content:
    content = content.replace(old_clients_btn, new_clients_btn)
    print("✅ Reverted sidebar badge")
else:
    print("⚠️ Sidebar badge pattern not found (might already be reverted)")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Stat cards removed")
print("✅ Timeline removed")
print("✅ index.html reverted to original overview")
