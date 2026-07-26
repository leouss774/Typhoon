"""
Compare view panel content between original GitHub index.html and current index.html
to find which view panels are missing or have been simplified.
"""
import re, os

CURRENT = 'index.html'
ORIGINAL = 'original_index.html'

# ── Extract view panel sections ─────────────────────────────
def extract_views(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all <section class="view-panel" id="view-xxx"> ... </section>
    pattern = r'(<section[^>]*class="view-panel"[^>]*id="(view-[^"]*)"[^>]*>.*?</section>)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    views = {}
    for full_html, view_id in matches:
        views[view_id] = full_html
    
    return views, content

original_views, _ = extract_views(ORIGINAL)
current_views, _ = extract_views(CURRENT)

print("=== VIEW PANEL COMPARISON ===")
print()

# Views in original but not in current (missing)
missing = set(original_views.keys()) - set(current_views.keys())
if missing:
    print(f"❌ MISSING from current ({len(missing)}):")
    for v in sorted(missing):
        print(f"  - {v} ({len(original_views[v])} chars)")
else:
    print("✅ All original view panels are present in current version")

# Views in current but not in original (new additions)
new_views = set(current_views.keys()) - set(original_views.keys())
if new_views:
    print(f"📦 NEW views in current ({len(new_views)}):")
    for v in sorted(new_views):
        print(f"  + {v} ({len(current_views[v])} chars)")

print()

# Compare content size for shared views
print("=== CONTENT SIZE COMPARISON ===")
for v in sorted(set(original_views.keys()) & set(current_views.keys())):
    orig_len = len(original_views[v])
    curr_len = len(current_views[v])
    diff = curr_len - orig_len
    status = "✅" if diff >= -50 else "⚠️"
    print(f"  {status} {v}: original={orig_len} chars, current={curr_len} chars (diff={diff:+d})")

print()

# For views with significant difference, show a summary
print("=== DETAILED ANALYSIS FOR SHORT VIEWS ===")
for v in sorted(set(original_views.keys()) & set(current_views.keys())):
    orig_len = len(original_views[v])
    curr_len = len(current_views[v])
    if curr_len < orig_len * 0.5:  # current is less than half the size
        print(f"\n⚠️  {v} is significantly shorter:")
        print(f"    Original ({orig_len} chars): first 200 chars = {original_views[v][:200]}")
        print(f"    Current  ({curr_len} chars): first 200 chars = {current_views[v][:200]}")
