"""Fix issues in view-assure-bien panel:
1. Escape < > in HTML text (build error)
2. Fix assureBannerPolicyTag → assureBannerPolicy
3. Add CSS for step navigation (afs-panel.active, afs-step.active/completed)
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Escape < and > in option text values (inside >TEXT<, not inside attributes)
# Only in the view-assure-bien section
idx = content.find('view-assure-bien')
section_start = content.rfind('<section', 0, idx)
section_end = content.find('</section>', section_start)
section_end = content.find('</section>', section_end + 10) + 10  # nested sections

before = content[:section_start]
section = content[section_start:section_end]
after_text = content[section_end:]

# Fix unescaped < and > in text content (not in tags or attributes)
import re

def escape_lt_gt_in_text(html):
    """Escape < and > that are in text content, not in tags or attributes."""
    result = []
    in_tag = False
    in_attr = False
    quote_char = None
    i = 0
    while i < len(html):
        ch = html[i]
        
        if ch == '<' and not in_tag:
            # Check if this starts a tag
            if i + 1 < len(html) and html[i+1] in ('/', '!', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'):
                in_tag = True
                result.append(ch)
            else:
                # This < is in text content, not starting a tag
                result.append('&lt;')
        elif ch == '>':
            if in_tag:
                # Could be end of tag
                in_tag = False
                result.append(ch)
            else:
                # > in text content
                result.append('&gt;')
        elif ch == '"' and in_tag:
            result.append(ch)
        elif ch == "'" and in_tag:
            result.append(ch)
        else:
            result.append(ch)
        i += 1
    
    return ''.join(result)

section_fixed = escape_lt_gt_in_text(section)

# 2. Fix ID: assureBannerPolicyTag → assureBannerPolicy
section_fixed = section_fixed.replace('id="assureBannerPolicyTag"', 'id="assureBannerPolicy"')

# Reassemble
new_content = before + section_fixed + after_text

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('✅ HTML fixes applied:')
print('  - Escaped < > in text content')
print('  - Renamed assureBannerPolicyTag → assureBannerPolicy')

# 3. Add CSS for step navigation to assure.css
with open('src/views/assure/assure.css', 'a', encoding='utf-8') as f:
    f.write("""
/* ── Form wizard steps ──────────────────────────────────────── */
.afs-panel { display: none !important; }
.afs-panel.active { display: flex !important; }

.afs-step {
  opacity: 0.4;
  transition: opacity 0.2s ease;
  cursor: default;
}
.afs-step.active { opacity: 1; }
.afs-step.completed { opacity: 0.6; }
.afs-step.completed .afs-step-num {
  background: #10b981;
  border-color: #10b981;
  color: #fff;
}

.afs-step-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid var(--border-color);
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
  transition: all 0.2s ease;
  margin-right: 4px;
}
.afs-step.active .afs-step-num {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: rgba(197,106,61,0.1);
}

.afs-step-label {
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 500;
}
.afs-step.active .afs-step-label {
  color: var(--text-primary);
}

/* ── Form fields ────────────────────────────────────────────── */
.afi-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.afi-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.afi-input,
.afi-select,
.afi-textarea {
  padding: 8px 10px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  background: var(--bg-panel);
  color: var(--text-primary);
  font-family: var(--font-primary);
  font-size: 13px;
  transition: border-color 0.2s ease;
  outline: none;
  width: 100%;
  box-sizing: border-box;
}

.afi-input:focus,
.afi-select:focus,
.afi-textarea:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(197,106,61,0.1);
}

.afi-textarea {
  resize: vertical;
  min-height: 60px;
}

.afi-check-label {
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
}

.afi-check-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--color-primary);
  cursor: pointer;
}

/* ── Panel header ────────────────────────────────────────────── */
.afs-panel-header h3 {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.afs-panel-header p {
  font-size: 12px;
  color: var(--text-muted);
}
""")

print('✅ Added form wizard CSS to assure.css')
