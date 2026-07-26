"""Upgrade the form step indicator in view-assure-bien from simple numbered circles
to a polished wizard with Material Symbols icons and arrow connectors.
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── The OLD step indicator HTML ─────────────────────────────────
OLD_STEPS = '''        <!-- Steps indicator -->
        <div class="afs-steps" style="display:flex;gap:4px;padding:4px 0;flex-shrink:0;">
          <div class="afs-step active" data-step="1"><span class="afs-step-num">1</span><span class="afs-step-label">Adresse</span></div>
          <div class="afs-step" data-step="2"><span class="afs-step-num">2</span><span class="afs-step-label">Structure</span></div>
          <div class="afs-step" data-step="3"><span class="afs-step-num">3</span><span class="afs-step-label">Toiture</span></div>
          <div class="afs-step" data-step="4"><span class="afs-step-num">4</span><span class="afs-step-label">Équipements</span></div>
          <div class="afs-step" data-step="5"><span class="afs-step-num">5</span><span class="afs-step-label">Finalisation</span></div>
        </div>'''

NEW_STEPS = '''        <!-- Steps indicator — Wizard with icons -->
        <div class="afs-wizard">
          <div class="afs-step active" data-step="1">
            <button type="button" class="afs-step-trigger">
              <span class="afs-step-icon"><span class="material-symbols-outlined">location_on</span></span>
              <span class="afs-step-label">Adresse</span>
            </button>
          </div>
          <div class="afs-step-arrow"><span class="material-symbols-outlined">chevron_right</span></div>
          <div class="afs-step" data-step="2">
            <button type="button" class="afs-step-trigger">
              <span class="afs-step-icon"><span class="material-symbols-outlined">foundation</span></span>
              <span class="afs-step-label">Structure</span>
            </button>
          </div>
          <div class="afs-step-arrow"><span class="material-symbols-outlined">chevron_right</span></div>
          <div class="afs-step" data-step="3">
            <button type="button" class="afs-step-trigger">
              <span class="afs-step-icon"><span class="material-symbols-outlined">roofing</span></span>
              <span class="afs-step-label">Toiture</span>
            </button>
          </div>
          <div class="afs-step-arrow"><span class="material-symbols-outlined">chevron_right</span></div>
          <div class="afs-step" data-step="4">
            <button type="button" class="afs-step-trigger">
              <span class="afs-step-icon"><span class="material-symbols-outlined">plumbing</span></span>
              <span class="afs-step-label">Équipements</span>
            </button>
          </div>
          <div class="afs-step-arrow"><span class="material-symbols-outlined">chevron_right</span></div>
          <div class="afs-step" data-step="5">
            <button type="button" class="afs-step-trigger">
              <span class="afs-step-icon"><span class="material-symbols-outlined">checklist</span></span>
              <span class="afs-step-label">Finalisation</span>
            </button>
          </div>
        </div>'''

# ── Replace in HTML ─────────────────────────────────────────────
if OLD_STEPS in content:
    content = content.replace(OLD_STEPS, NEW_STEPS)
    print('✅ Step indicator replaced with wizard icons')
else:
    print('⚠️  Old step indicator not found — trying alternate format...')
    # Try to find the afs-steps div
    idx = content.find('afs-steps')
    if idx > 0:
        # Find the div and its content
        div_start = content.rfind('<div', idx-10, idx)
        if div_start > 0:
            # Find the closing div
            depth = 0
            i = content.find('>', div_start) + 1
            while i < len(content):
                if content[i:i+4] == '<div':
                    depth += 1
                    i = content.find('>', i) + 1
                elif content[i:i+11] == '</div>':
                    if depth == 0:
                        div_end = i + 11
                        break
                    depth -= 1
                    i = i + 11
                else:
                    i += 1
            old_div = content[div_start:div_end]
            print(f'Found old steps div: {len(old_div)} chars')
            content = content.replace(old_div, NEW_STEPS)
            print('✅ Replaced!')
    else:
        print('❌ Could not find steps indicator at all')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ index.html updated')
