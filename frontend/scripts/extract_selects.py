"""Extract select option values for both forms"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find assured form selects
print("=== ASSURED FORM (afi_) SELECTS ===")
afi_selects = re.findall(r'<select[^>]*id="(afi_\w+)"[^>]*class="afi-select"[^>]*>(.*?)</select>', content, re.DOTALL)
for id, options_html in afi_selects:
    options = re.findall(r'<option value="([^"]*)"[^>]*>(.*?)</option>', options_html)
    print(f"\n{id}:")
    for val, label in options:
        print(f"  {val} -> {label.strip()}")

print("\n\n=== ACTUARIAL FORM (expert) SELECTS ===")
expert_selects = re.findall(r'<select[^>]*id="(expert\w+)"[^>]*class="risk-expert-select"[^>]*>(.*?)</select>', content, re.DOTALL)
for id, options_html in expert_selects:
    options = re.findall(r'<option value="([^"]*)"[^>]*>(.*?)</option>', options_html)
    print(f"\n{id}:")
    for val, label in options:
        print(f"  {val} -> {label.strip()}")
