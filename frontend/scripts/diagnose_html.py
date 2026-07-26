"""Diagnose the HTML file to find what's missing."""
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Find all view panel IDs  
ids = re.findall(r'id="(view-[^"]*)"', content)
print("=== VIEW PANELS REMAINING ===")
for v in ids:
    print(f"  {v}")

print()

# Find all section tags
sections = re.findall(r'<section', content)
section_closes = re.findall(r'</section>', content)
print(f"<section>: {len(sections)}")
print(f"</section>: {len(section_closes)}")
print(f"Balance: {len(sections) - len(section_closes)}")

# Find the problematic area - after the overview view
# Look for the transition from overview to next view
overview_end = content.find('<!-- ====== VIEW: Portfolio')
if overview_end == -1:
    overview_end = content.find('view-portfolio')
if overview_end == -1:
    # Check if there's any view- after overview
    overview_pos = content.find('view-overview')
    rest = content[overview_pos:]
    next_view = rest.find('view-panel')
    if next_view > 0:
        print(f"\nContent AFTER view-overview (first 500 chars):")
        print(repr(rest[next_view-100:next_view+400]))
    else:
        print("\nNo view-panel found after view-overview!")
        print(f"Last 500 chars of file:")
        print(repr(content[-500:]))
else:
    print(f"\nPortfolio view starts at position {overview_end}")

# Check for key sections
for key in ['view-portfolio', 'view-property-risk', 'view-clients', 'view-settings', 
            'view-assure-bien', 'view-assure-travaux', 'view-assure-engagement', 'view-assure-dossier',
            'property-risk', 'portfolioGrid', 'clientsTableBody']:
    if key in content:
        print(f"  ✅ {key} found")
    else:
        print(f"  ❌ {key} MISSING!")
