"""Add role-specific settings navigation items and view panels to index.html."""

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, '..', 'index.html'), 'r', encoding='utf-8') as f:
    content = f.read()

# ─── Step 1: Replace shared settings nav item with 4 role-specific ones ───

old_nav = '''          <!-- Shared Settings -->
          <button class="nav-item" data-view="settings" aria-label="Settings">
            <span class="material-symbols-outlined">settings</span>
            <span class="nav-label">Settings</span>
            <md-ripple></md-ripple>
          </button>'''

new_nav = '''          <!-- Settings by role -->
          <button class="nav-item nav-role-assureur" data-view="settings" aria-label="Paramètres">
            <span class="material-symbols-outlined">settings</span>
            <span class="nav-label">Paramètres</span>
            <md-ripple></md-ripple>
          </button>
          <button class="nav-item nav-role-assure" data-view="assure-settings" aria-label="Paramètres" style="display:none;">
            <span class="material-symbols-outlined">settings</span>
            <span class="nav-label">Paramètres</span>
            <md-ripple></md-ripple>
          </button>
          <button class="nav-item nav-role-expert" data-view="expert-settings" aria-label="Paramètres" style="display:none;">
            <span class="material-symbols-outlined">settings</span>
            <span class="nav-label">Paramètres</span>
            <md-ripple></md-ripple>
          </button>
          <button class="nav-item nav-role-admin" data-view="admin-settings" aria-label="Paramètres" style="display:none;">
            <span class="material-symbols-outlined">settings</span>
            <span class="nav-label">Paramètres</span>
            <md-ripple></md-ripple>
          </button>'''

if old_nav in content:
    content = content.replace(old_nav, new_nav, 1)
    print('[OK] Replaced shared settings nav with 4 role-specific nav items')
else:
    print('[FAIL] Could not find shared settings nav item')

# ─── Step 2: Add new view panels for assure-settings, expert-settings, admin-settings ───
# The existing settings panel (view-settings) ends with </section> before the auth views.
# We'll insert new panels right after the existing settings panel closes.

# Find the settings closing tag that's followed by auth views
marker = '        <!-- ====== VIEW: Assureur - Expert Management ====== -->'
if marker in content:
    idx = content.index(marker)
    before = content[:idx]
    last_section_close = before.rstrip().rfind('</section>')
    if last_section_close > 0:
        settings_end = last_section_close + len('</section>')
        
        new_panels = '''

        <!-- ====== VIEW: Assuré Settings ====== -->
        <section class=\"view-panel\" id=\"view-assure-settings\">
          <div class=\"settings-tab-content active\" data-content=\"account\">
            <div class=\"settings-card\">
              <div class=\"settings-card-body\">
                <div class=\"settings-avatar-row\">
                  <img src=\"https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=100&q=80\" alt=\"user-avatar\" class=\"settings-avatar-img\" id=\"settingsAvatarAssure\">
                  <div class=\"settings-avatar-actions\">
                    <label for=\"settingsAvatarInputAssure\" class=\"settings-btn settings-btn-primary\" tabindex=\"0\">
                      <span class=\"material-symbols-outlined\" style=\"font-size:16px!important;\">upload</span>
                      <span>Télécharger une photo</span>
                      <input type=\"file\" id=\"settingsAvatarInputAssure\" class=\"settings-hidden-input\" accept=\"image/*\">
                    </label>
                    <button type=\"button\" class=\"settings-btn settings-btn-secondary\" id=\"settingsAvatarResetAssure\">
                      <span class=\"material-symbols-outlined\" style=\"font-size:16px!important;\">refresh</span>
                      <span>Réinitialiser</span>
                    </button>
                    <div class=\"settings-avatar-hint\">Formats JPG, GIF ou PNG. Taille max 800K</div>
                  </div>
                </div>
                <form class=\"settings-form-grid\">
                  <div class=\"settings-form-group\">
                    <label class=\"settings-form-label\">Prénom</label>
                    <input type=\"text\" class=\"settings-form-input\" value=\"Marie\" placeholder=\"Prénom\">
                  </div>
                  <div class=\"settings-form-group\">
                    <label class=\"settings-form-label\">Nom</label>
                    <input type=\"text\" class=\"settings-form-input\" value=\"Dubois\" placeholder=\"Nom\">
                  </div>
                  <div class=\"settings-form-group\">
                    <label class=\"settings-form-label\">Email</label>
                    <input type=\"email\" class=\"settings-form-input\" value=\"marie.dubois@email.fr\" placeholder=\"email\">
                  </div>
                  <div class=\"settings-form-group\">
                    <label class=\"settings-form-label\">Téléphone</label>
                    <input type=\"tel\" class=\"settings-form-input\" value=\"6 98 76 54 32\" placeholder=\"Téléphone\">
                  </div>
                  <div class=\"settings-form-group\">
                    <label class=\"settings-form-label\">Adresse</label>
                    <input type=\"text\" class=\"settings-form-input\" value=\"8 Rue de la Paix\" placeholder=\"Adresse\">
                  </div>
                  <div class=\"settings-form-group\">
                    <label class=\"settings-form-label\">Ville</label>
                    <input type=\"text\" class=\"settings-form-input\" value=\"Paris\" placeholder=\"Ville\">
                  </div>
                  <div class=\"settings-form-group\">
                    <label class=\"settings-form-label\">Code Postal</label>
                    <input type=\"text\" class=\"settings-form-input\" value=\"75002\" placeholder=\"75002\" maxlength=\"6\">
                  </div>
                  <div class=\"settings-form-group\">
                    <label class=\"settings-form-label\">Pays</label>
                    <select class=\"settings-form-select\">
                      <option value=\"FR\" selected>France</option>
                      <option value=\"BE\">Belgique</option>
                    </select>
                  </div>
                  <div class=\"settings-form-actions\">
                    <button type=\"submit\" class=\"settings-btn settings-btn-primary\" id=\"settingsAccountSave\">
                      <span class=\"material-symbols-outlined\" style=\"font-size:16px!important;\">save</span>
                      Enregistrer
                    </button>
                    <button type=\"button\" class=\"settings-btn\" id=\"settingsAccountCancel\">
                      Annuler
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </section>

        <!-- ====== VIEW: Expert Settings ====== -->
        <section class=\"view-panel\" id=\"view-expert-settings\">
          <div class=\"settings-tab-content active\" data-content=\"account\">
            <div class=\"settings-card\">
              <div class=\"settings-card-body\">
                <div class=\"settings-avatar-row\">
                  <img src=\"https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=100&q=80\" alt=\"user-avatar\" class=\"settings-avatar-img\" id=\"settingsAvatarExpert\">
                  <div class=\"settings-avatar-actions\">
                    <label for=\"settingsAvatarInputExpert\" class=\"settings-btn settings-btn-primary\" tabindex=\"0\">
                      <span class=\"material-symbols-outlined\" style=\"font-size:16px!important;\">upload</span>
                      <span>Télécharger une photo</span>
                      <input type=\"file\" id=\"settingsAvatarInputExpert\" class=\"settings-hidden-input\" accept=\"image/*\">
                    </label>
                    <button type=\"button\" class=\"settings-btn settings-btn-secondary\" id=\"settingsAvatarResetExpert\">
                      <span class=\"material-symbols-outlined\" style=\"font-size:16px!important;\">refresh</span>
                      <span>Réinitialiser</span>
                    </button>
                    <div class=\"settings-avatar-hint\">Formats JPG, GIF ou PNG. Taille max 800K</div>
                  </div>
                </div>
                <form class=\"settings-form-grid\">
                  <div class=\"settings-form-group\">
                    <label class=\"settings-form-label\">Prénom</label>
                    <input type=\"text\" class=\"settings-form-input\" value=\"Thomas\" placeholder=\"Prénom\">
                  </div>
                  <div class=\"settings-form-group\">
                    <label class=\"settings-form-label\">Nom</label>
                    <input type=\"text\" class=\"settings-form-input\" value=\"Bernard\" placeholder=\"Nom\">
                  </div>
                  <div class=\"settings-form-group\">
                    <label class=\"settings-form-label\">Email</label>
                    <input type=\"email\" class=\"settings-form-input\" value=\"thomas.bernard@expert.fr\" placeholder=\"email\">
                  </div>
                  <div class=\"settings-form-group\">
                    <label class=\"settings-form-label\">Téléphone</label>
                    <input type=\"tel\" class=\"settings-form-input\" value=\"6 11 22 33 44\" placeholder=\"Téléphone\">
                  </div>
                  <div class=\"settings-form-actions\">
                    <button type=\"submit\" class=\"settings-btn settings-btn-primary\" id=\"settingsAccountSave\">
                      <span class=\"material-symbols-outlined\" style=\"font-size:16px!important;\">save</span>
                      Enregistrer
                    </button>
                    <button type=\"button\" class=\"settings-btn\" id=\"settingsAccountCancel\">
                      Annuler
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </section>

        <!-- ====== VIEW: Admin Settings ====== -->
        <section class=\"view-panel\" id=\"view-admin-settings\">
          <div class=\"settings-tab-content active\" data-content=\"account\">
            <div class=\"settings-card\">
              <div class=\"settings-card-body\">
                <div class=\"settings-avatar-row\">
                  <img src=\"https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=100&q=80\" alt=\"user-avatar\" class=\"settings-avatar-img\" id=\"settingsAvatarAdmin\">
                  <div class=\"settings-avatar-actions\">
                    <label for=\"settingsAvatarInputAdmin\" class=\"settings-btn settings-btn-primary\" tabindex=\"0\">
                      <span class=\"material-symbols-outlined\" style=\"font-size:16px!important;\">upload</span>
                      <span>Télécharger une photo</span>
                      <input type=\"file\" id=\"settingsAvatarInputAdmin\" class=\"settings-hidden-input\" accept=\"image/*\">
                    </label>
                    <button type=\"button\" class=\"settings-btn settings-btn-secondary\" id=\"settingsAvatarResetAdmin\">
                      <span class=\"material-symbols-outlined\" style=\"font-size:16px!important;\">refresh</span>
                      <span>Réinitialiser</span>
                    </button>
                    <div class=\"settings-avatar-hint\">Formats JPG, GIF ou PNG. Taille max 800K</div>
                  </div>
                </div>
                <form class=\"settings-form-grid\">
                  <div class=\"settings-form-group\">
                    <label class=\"settings-form-label\">Prénom</label>
                    <input type=\"text\" class=\"settings-form-input\" value=\"Admin\" placeholder=\"Prénom\">
                  </div>
                  <div class=\"settings-form-group\">
                    <label class=\"settings-form-label\">Nom</label>
                    <input type=\"text\" class=\"settings-form-input\" value=\"Prévia\" placeholder=\"Nom\">
                  </div>
                  <div class=\"settings-form-group\">
                    <label class=\"settings-form-label\">Email</label>
                    <input type=\"email\" class=\"settings-form-input\" value=\"admin@previa.fr\" placeholder=\"email\">
                  </div>
                  <div class=\"settings-form-group\">
                    <label class=\"settings-form-label\">Téléphone</label>
                    <input type=\"tel\" class=\"settings-form-input\" value=\"6 00 11 22 33\" placeholder=\"Téléphone\">
                  </div>
                  <div class=\"settings-form-actions\">
                    <button type=\"submit\" class=\"settings-btn settings-btn-primary\" id=\"settingsAccountSave\">
                      <span class=\"material-symbols-outlined\" style=\"font-size:16px!important;\">save</span>
                      Enregistrer
                    </button>
                    <button type=\"button\" class=\"settings-btn\" id=\"settingsAccountCancel\">
                      Annuler
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </section>
'''

        content = content[:settings_end] + new_panels + content[settings_end:]
        print(f'[OK] Added 3 new settings view panels after line {content[:settings_end].count(chr(10)) + 1}')
    else:
        print('[FAIL] Could not find settings closing </section>')
else:
    print('[FAIL] Could not find auth section marker')

with open(os.path.join(script_dir, '..', 'index.html'), 'w', encoding='utf-8') as f:
    f.write(content)

print('\nDone!')
