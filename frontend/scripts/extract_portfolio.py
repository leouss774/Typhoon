"""Extract the portfolio HTML section from index.html."""
import os, re
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..')
html_path = os.path.join(project_root, 'index.html')

with open(html_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_portfolio = False
depth = 0
for i, line in enumerate(lines):
    stripped = line.strip()
    if 'id="view-portfolio"' in stripped:
        in_portfolio = True
    if in_portfolio:
        print(f"{i+1}: {stripped[:150]}")
        if '<section' in stripped and 'id="view-portfolio"' in stripped:
            depth = 1
        elif '<section' in stripped and '</section>' not in stripped:
            depth += 1
        elif '</section>' in stripped and '<section' not in stripped:
            depth -= 1
            if depth <= 0:
                print(f"{i+1}: {stripped[:150]}")
                break
