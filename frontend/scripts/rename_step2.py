"""Rename step 2 'Expert' -> 'Actuariat' in index.html"""
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# Replace in risk-step
old = 'data-step="expert">\n                    <span class="risk-step-circle">2</span>\n                    <div class="risk-step-text">\n                      <span class="risk-step-name">Expert</span>\n                      <span class="risk-step-desc">Envoi expert + questionnaire technique</span>'
new = 'data-step="actuariat">\n                    <span class="risk-step-circle">2</span>\n                    <div class="risk-step-text">\n                      <span class="risk-step-name">Actuariat</span>\n                      <span class="risk-step-desc">Questionnaire technique + calcul score</span>'
if old in content:
    content = content.replace(old, new)
    changes += 1
    print('OK: Updated risk-step expert -> actuariat')
else:
    print('FAIL: Could not find risk-step expert')

# Replace in risk-tab-content
old2 = 'data-content="expert">\n            <div class="risk-expert-layout">'
new2 = 'data-content="actuariat">\n            <div class="risk-expert-layout">'
if old2 in content:
    content = content.replace(old2, new2)
    changes += 1
    print('OK: Updated risk-tab-content expert -> actuariat')
else:
    print('FAIL: Could not find risk-tab-content expert')

# Update expert nav items labels
# Expert clients
old3 = 'data-view="expert-clients" aria-label="Clients"'
new3 = 'data-view="expert-clients" aria-label="Mes clients"'
if old3 in content:
    content = content.replace(old3, new3)
    changes += 1
    print('OK: Updated expert nav label: Clients -> Mes clients')
else:
    print('FAIL: Could not find expert-clients nav item')

# Expert portfolio
old4 = 'data-view="expert-portfolio" aria-label="Portefeuille"'
new4 = 'data-view="expert-portfolio" aria-label="Mon portefeuille"'
if old4 in content:
    content = content.replace(old4, new4)
    changes += 1
    print('OK: Updated expert nav label: Portefeuille -> Mon portefeuille')
else:
    print('FAIL: Could not find expert-portfolio nav item')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nDone: {changes} changes made')
