"""
Remove remaining expert view panels and modals from index.html by line ranges.
"""
with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines to remove (0-indexed):
# experts view: 2154 to 2254 (section starts at 2154, next section at 2255)
# expert-dashboard view: 2255 to 2363 (section starts at 2255, next at 2363)
# missions view: 2363 to 2419 (section starts at 2363, next at 2419)
# inviteExpertModal: 3494 to ~3531 (need to find)
# assignExpertModal: 3531 to ~3565 (need to find)

# Find exact boundaries by looking for 'section' or 'modal' transitions
removed_ranges = []

# 1. Remove experts view panel
for i in range(2153, 2155):
    if 'view-experts' in lines[i]:
        # Find end: next "view-panel" or end of view-experts
        for j in range(i, min(i + 200, len(lines))):
            if j > i and ('id="view-' in lines[j] or '<!-- ======' in lines[j]):
                # Remove from i to j-1
                removed_ranges.append((i, j - 1))
                print(f"[OK] Experts view panel: lines {i+1}-{j}")
                break
        break

# 2. Remove expert-dashboard view panel
for i in range(2253, 2257):
    if i < len(lines) and 'view-expert-dashboard' in lines[i]:
        for j in range(i, min(i + 200, len(lines))):
            if j > i and ('id="view-' in lines[j] or '<!-- ======' in lines[j]):
                removed_ranges.append((i, j - 1))
                print(f"[OK] Expert dashboard view panel: lines {i+1}-{j}")
                break
        break

# 3. Remove missions view panel
for i in range(2361, 2365):
    if i < len(lines) and 'view-missions' in lines[i]:
        for j in range(i, min(i + 200, len(lines))):
            if j > i and ('id="view-' in lines[j] or '<!-- ======' in lines[j]):
                removed_ranges.append((i, j - 1))
                print(f"[OK] Missions view panel: lines {i+1}-{j}")
                break
        break

# 4. Remove invite expert modal
for i in range(3492, 3496):
    if i < len(lines) and 'inviteExpertModal' in lines[i]:
        # Find 3 closing </div> tags to close the modal
        close_count = 0
        for j in range(i, min(i + 80, len(lines))):
            if '</div>' in lines[j]:
                close_count += 1
                if close_count >= 3:
                    removed_ranges.append((i, j))
                    print(f"[OK] Invite expert modal: lines {i+1}-{j+1}")
                    break
        break

# 5. Remove assign expert modal
for i in range(3529, 3533):
    if i < len(lines) and 'assignExpertModal' in lines[i]:
        close_count = 0
        for j in range(i, min(i + 80, len(lines))):
            if '</div>' in lines[j]:
                close_count += 1
                if close_count >= 3:
                    removed_ranges.append((i, j))
                    print(f"[OK] Assign expert modal: lines {i+1}-{j+1}")
                    break
        break

# Sort ranges in reverse order (so we remove from bottom to top to preserve indices)
removed_ranges.sort(key=lambda x: x[0], reverse=True)

for start, end in removed_ranges:
    del lines[start:end + 1]

with open('index.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"\n[OK] Total lines removed: {sum(e - s + 1 for s, e in removed_ranges)}")
