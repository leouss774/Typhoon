"""Fix remaining 'Expert' step reference in index.html"""
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''data-step="expert">
              <span class="risk-step-circle">2</span>
              <div class="risk-step-text">
                <span class="risk-step-name">Expert</span>
                <span class="risk-step-desc">Évaluation sur place</span>'''

new = '''data-step="actuariat">
              <span class="risk-step-circle">2</span>
              <div class="risk-step-text">
                <span class="risk-step-name">Actuariat</span>
                <span class="risk-step-desc">Questionnaire technique + calcul score</span>'''

if old in content:
    content = content.replace(old, new)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK: Updated risk-step expert -> actuariat')
else:
    print('FAIL: Could not find the pattern')
    # Debug: find what's there
    idx = content.find('risk-step-circle'
    if idx >= 0:
        start = max(0, idx - 200)
        end = min(len(content), idx + 200)
        print('Found near:', repr(content[start:end]))
