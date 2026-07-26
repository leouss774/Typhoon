"""Remove the 3 extra settings view panels (assure-settings, expert-settings, admin-settings) from index.html."""
import os
import re

script_dir = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(script_dir, '..', 'index.html')

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove 3 new settings view panels using regex
# Match from opening comment through closing section tag
panels = [
    r'<!-- ====== VIEW: Assuré Settings ====== -->.*?</section>',
    r'<!-- ====== VIEW: Expert Settings ====== -->.*?</section>',
    r'<!-- ====== VIEW: Admin Settings ====== -->.*?</section>',
]

for pattern in panels:
    before = len(content)
    content = re.sub(pattern, '', content, count=1, flags=re.DOTALL)
    removed = before - len(content)
    if removed > 0:
        print('[OK] Removed panel - {0} chars'.format(removed))
    else:
        print('[FAIL] Pattern not found')

# Clean up extra blank lines
content = re.sub(r'\n\s*\n\s*\n\s*\n', '\n\n', content)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('\nDone!')
