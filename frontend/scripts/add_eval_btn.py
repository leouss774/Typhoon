"""Add 'Évaluer ce bien' button to the client detail panel in index.html"""
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the cdp-profile-actions section for client detail (the one with cdpEditToggle)
# We need to add the evaluate button before cdpEditToggle
old = '''                <div class="cdp-profile-actions">
                  <button class="cdp-btn cdp-btn-outline" id="cdpEditToggle">
                    <span class="material-symbols-outlined" style="font-size:16px!important;">edit</span>
                    Modifier
                  </button>'''

new = '''                <div class="cdp-profile-actions">
                  <button class="cdp-btn cdp-btn-primary" id="cdpEvaluateBtn" title="Lancer l'évaluation des risques">
                    <span class="material-symbols-outlined" style="font-size:16px!important;">gps_fixed</span>
                    Évaluer ce bien
                  </button>
                  <button class="cdp-btn cdp-btn-outline" id="cdpEditToggle">
                    <span class="material-symbols-outlined" style="font-size:16px!important;">edit</span>
                    Modifier
                  </button>'''

if old in content:
    content = content.replace(old, new, 1)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Added Évaluer button to client detail panel')
else:
    print('❌ Could not find the target HTML. Searching for partial match...')
    # Debug: find approximate location
    idx = content.find('cdpEditToggle')
    if idx >= 0:
        print(f'Found cdpEditToggle at position {idx}')
        print(content[idx-200:idx+100])
    else:
        idx = content.find('cdp-profile-actions')
        if idx >= 0:
            print(f'Found cdp-profile-actions at position {idx}')
            print(content[idx:idx+300])
