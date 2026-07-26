"""Remove the duplicate view-overview panel (second occurrence)."""
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the SECOND occurrence of view-overview
first_idx = content.find('id="view-overview"')
second_idx = content.find('id="view-overview"', first_idx + 50)

if second_idx < 0:
    print("❌ Second view-overview not found")
    exit(1)

# Find section start
section_start = content.rfind('<section', 0, second_idx)
if section_start < 0:
    print("❌ Could not find section start")
    exit(1)

# Find closing section by tracking depth
after = content[section_start:]
depth = 1
i = after.find('>', 50) + 1
while i < len(after) and depth > 0:
    next_open = after.find('<section', i)
    next_close = after.find('</section>', i)
    if next_close == -1:
        print("❌ Could not find closing section")
        exit(1)
    if next_open != -1 and next_open < next_close:
        depth += 1
        i = after.find('>', next_open) + 1
    else:
        depth -= 1
        i = next_close + 10

section_end = section_start + i
removed_len = section_end - section_start

# Remove it
content = content[:section_start] + content[section_end:]
print(f"✅ Removed duplicate view-overview ({removed_len} chars, from pos {section_start} to {section_end})")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
count = content.count('id="view-overview"')
print(f"✅ view-overview occurrences remaining: {count}")
