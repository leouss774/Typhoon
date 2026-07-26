"""
Add inline JS click handlers for admin/expert settings tabs,
and update router for admin/expert roles.
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the end of the dashboard section - right before the Webflow scripts
# Insert a small script block before the Webflow scripts section
insert_marker = '    <!-- Webflow / Landing scripts -->'
tab_script = '''    <!-- Inline tab handlers for admin/expert settings -->
    <script>
      // Admin settings tabs
      document.addEventListener('DOMContentLoaded', function() {
        document.querySelectorAll('#adminSettingsTabs .settings-tab').forEach(function(tab) {
          tab.addEventListener('click', function() {
            document.querySelectorAll('#adminSettingsTabs .settings-tab').forEach(function(t) { t.classList.remove('active'); });
            this.classList.add('active');
            var target = this.getAttribute('data-stab');
            document.querySelectorAll('#view-admin-settings .settings-content').forEach(function(c) { c.classList.remove('active'); });
            var targetEl = document.querySelector('#view-admin-settings .settings-content[data-scontent="' + target + '"]');
            if (targetEl) targetEl.classList.add('active');
          });
        });
        // Expert settings tabs
        document.querySelectorAll('#expertSettingsTabs .settings-tab').forEach(function(tab) {
          tab.addEventListener('click', function() {
            document.querySelectorAll('#expertSettingsTabs .settings-tab').forEach(function(t) { t.classList.remove('active'); });
            this.classList.add('active');
            var target = this.getAttribute('data-stab');
            document.querySelectorAll('#view-expert-settings .settings-content').forEach(function(c) { c.classList.remove('active'); });
            var targetEl = document.querySelector('#view-expert-settings .settings-content[data-scontent="' + target + '"]');
            if (targetEl) targetEl.classList.add('active');
          });
        });
      });
    </script>
'''

if insert_marker in content:
    content = content.replace(insert_marker, tab_script + '\n' + insert_marker)
    print("✅ Admin/expert tab handlers added")
else:
    print("⚠️ Could not find insertion point")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Done")
