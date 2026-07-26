"""Rebuild all auth panels in index.html with modern split-screen layout matching auth.css.

This script:
1. Replaces the old basic view-auth-sign-in with a modern auth-sign-in panel
2. Adds auth-sign-up, auth-forgot-password, auth-reset-password, auth-two-step panels
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── The modern auth panels HTML ──────────────────────────────────

AUTH_PANELS = '''    <!-- ====== AUTH ====== -->
    <!-- SIGN IN -->
    <section class="auth-view" id="auth-sign-in" style="display:none;">
      <div class="auth-cover-layout">
        <div class="auth-cover-panel">
          <div class="auth-cover-brand">
            <div class="logo-icon"><span class="material-symbols-outlined">auto_awesome</span></div>
            <span>Prévia</span>
          </div>
          <div class="auth-cover-content">
            <div class="auth-cover-illustration">
              <span class="material-symbols-outlined">verified_user</span>
              <div class="ring-1"></div>
              <div class="ring-2"></div>
            </div>
            <h2>Bienvenue sur<br/>Prévia Risk Platform</h2>
            <p>Plateforme d'évaluation et de gestion des risques assurantiels. Analysez, évaluez et pilotez vos risques en temps réel.</p>
          </div>
        </div>
        <div class="auth-form-panel">
          <div class="auth-form-card">
            <div class="auth-form-header">
              <div class="auth-badge"><span class="material-symbols-outlined">lock</span> Espace professionnel</div>
              <h3>Connexion</h3>
              <p>Accédez à votre tableau de bord en vous connectant à votre compte.</p>
            </div>
            <form onsubmit="return false;">
              <div class="auth-input-group">
                <span class="material-symbols-outlined input-icon">email</span>
                <input type="email" name="email" placeholder="Adresse email" autocomplete="email" required>
              </div>
              <div class="auth-input-group">
                <span class="material-symbols-outlined input-icon">lock</span>
                <input type="password" name="password" placeholder="Mot de passe" autocomplete="current-password" required>
                <button type="button" class="input-toggle"><span class="material-symbols-outlined">visibility</span></button>
              </div>
              <div class="auth-check-row">
                <label class="auth-check-label"><input type="checkbox" name="remember"> Se souvenir de moi</label>
                <a class="auth-link" data-auth-target="forgot-password">Mot de passe oublié ?</a>
              </div>
              <button type="submit" class="auth-submit-btn" data-action="sign-in"><span class="material-symbols-outlined">login</span> Se connecter</button>
            </form>
            <div class="auth-divider">ou</div>
            <div class="auth-social-row">
              <button type="button" class="auth-social-btn" data-action="magic-link"><svg class="social-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 4L8 12l12 8V4z"/></svg> Lien magique</button>
              <button type="button" class="auth-social-btn" data-action="google"><svg class="social-icon" viewBox="0 0 24 24"><path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg> Google</button>
            </div>
            <div class="auth-footer-text">Vous n'avez pas de compte ? <a class="auth-link" data-auth-target="sign-up">Créer un compte</a></div>
          </div>
        </div>
      </div>
    </section>

    <!-- SIGN UP -->
    <section class="auth-view" id="auth-sign-up" style="display:none;">
      <div class="auth-cover-layout">
        <div class="auth-cover-panel">
          <div class="auth-cover-brand">
            <div class="logo-icon"><span class="material-symbols-outlined">auto_awesome</span></div>
            <span>Prévia</span>
          </div>
          <div class="auth-cover-content">
            <div class="auth-cover-illustration">
              <span class="material-symbols-outlined">how_to_reg</span>
              <div class="ring-1"></div>
              <div class="ring-2"></div>
            </div>
            <h2>Rejoignez<br/>Prévia Risk Platform</h2>
            <p>Créez votre compte en quelques secondes et commencez à gérer vos évaluations de risques.</p>
          </div>
        </div>
        <div class="auth-form-panel">
          <div class="auth-form-card">
            <div class="auth-form-header">
              <div class="auth-badge"><span class="material-symbols-outlined">person_add</span> Inscription</div>
              <h3>Créer un compte</h3>
              <p>Remplissez les informations ci-dessous pour créer votre espace professionnel.</p>
            </div>
            <form onsubmit="return false;">
              <div class="auth-input-group">
                <span class="material-symbols-outlined input-icon">person</span>
                <input type="text" name="fullName" placeholder="Nom complet" autocomplete="name" required>
              </div>
              <div class="auth-input-group">
                <span class="material-symbols-outlined input-icon">email</span>
                <input type="email" name="email" placeholder="Adresse email" autocomplete="email" required>
              </div>
              <div class="auth-input-group">
                <span class="material-symbols-outlined input-icon">lock</span>
                <input type="password" name="password" placeholder="Mot de passe" autocomplete="new-password" required>
                <button type="button" class="input-toggle"><span class="material-symbols-outlined">visibility</span></button>
              </div>
              <div class="auth-strength" id="authPasswordStrength">
                <div class="auth-strength-bar"></div>
                <div class="auth-strength-bar"></div>
                <div class="auth-strength-bar"></div>
              </div>
              <div class="auth-strength-label" id="authStrengthLabel"></div>
              <div class="auth-check-row" style="margin-top:16px;">
                <label class="auth-check-label"><input type="checkbox" name="terms" required> J'accepte les <a class="auth-link" style="font-size:12px;">conditions d'utilisation</a></label>
              </div>
              <button type="submit" class="auth-submit-btn" data-action="sign-up" style="margin-top:8px;"><span class="material-symbols-outlined">person_add</span> Créer mon compte</button>
            </form>
            <div class="auth-divider">ou</div>
            <div class="auth-social-row">
              <button type="button" class="auth-social-btn" data-action="google"><svg class="social-icon" viewBox="0 0 24 24"><path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg> Google</button>
              <button type="button" class="auth-social-btn" data-action="magic-link"><svg class="social-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 4L8 12l12 8V4z"/></svg> Lien magique</button>
            </div>
            <div class="auth-footer-text">Déjà un compte ? <a class="auth-link" data-auth-target="sign-in">Se connecter</a></div>
          </div>
        </div>
      </div>
    </section>

    <!-- FORGOT PASSWORD -->
    <section class="auth-view" id="auth-forgot-password" style="display:none;">
      <div class="auth-cover-layout">
        <div class="auth-cover-panel">
          <div class="auth-cover-brand">
            <div class="logo-icon"><span class="material-symbols-outlined">auto_awesome</span></div>
            <span>Prévia</span>
          </div>
          <div class="auth-cover-content">
            <div class="auth-cover-illustration">
              <span class="material-symbols-outlined">help_center</span>
              <div class="ring-1"></div>
              <div class="ring-2"></div>
            </div>
            <h2>Mot de passe<br/>oublié ?</h2>
            <p>Pas d'inquiétude. Saisissez votre email et nous vous enverrons un lien de réinitialisation.</p>
          </div>
        </div>
        <div class="auth-form-panel">
          <div class="auth-form-card">
            <div class="auth-form-header">
              <div class="auth-badge"><span class="material-symbols-outlined">lock_reset</span> Réinitialisation</div>
              <h3>Mot de passe oublié</h3>
              <p>Saisissez l'adresse email associée à votre compte pour recevoir un lien de réinitialisation.</p>
            </div>
            <form onsubmit="return false;">
              <div class="auth-input-group">
                <span class="material-symbols-outlined input-icon">email</span>
                <input type="email" name="email" placeholder="Adresse email" autocomplete="email" required>
              </div>
              <button type="submit" class="auth-submit-btn"><span class="material-symbols-outlined">send</span> Envoyer le lien</button>
            </form>
            <div class="auth-footer-text"><a class="auth-link" data-auth-target="sign-in"><span class="material-symbols-outlined" style="font-size:14px!important;vertical-align:middle;">arrow_back</span> Retour à la connexion</a></div>
          </div>
        </div>
      </div>
    </section>

    <!-- RESET PASSWORD -->
    <section class="auth-view" id="auth-reset-password" style="display:none;">
      <div class="auth-cover-layout">
        <div class="auth-cover-panel">
          <div class="auth-cover-brand">
            <div class="logo-icon"><span class="material-symbols-outlined">auto_awesome</span></div>
            <span>Prévia</span>
          </div>
          <div class="auth-cover-content">
            <div class="auth-cover-illustration">
              <span class="material-symbols-outlined">key</span>
              <div class="ring-1"></div>
              <div class="ring-2"></div>
            </div>
            <h2>Nouveau<br/>mot de passe</h2>
            <p>Choisissez un mot de passe sécurisé pour protéger votre compte.</p>
          </div>
        </div>
        <div class="auth-form-panel">
          <div class="auth-form-card">
            <div class="auth-form-header">
              <div class="auth-badge"><span class="material-symbols-outlined">password</span> Réinitialisation</div>
              <h3>Nouveau mot de passe</h3>
              <p>Choisissez un mot de passe sécurisé d'au moins 8 caractères.</p>
            </div>
            <form onsubmit="return false;">
              <div class="auth-input-group">
                <span class="material-symbols-outlined input-icon">lock</span>
                <input type="password" name="password" placeholder="Nouveau mot de passe" autocomplete="new-password" required>
                <button type="button" class="input-toggle"><span class="material-symbols-outlined">visibility</span></button>
              </div>
              <div class="auth-input-group">
                <span class="material-symbols-outlined input-icon">lock</span>
                <input type="password" name="confirmPassword" placeholder="Confirmer le mot de passe" autocomplete="new-password" required>
                <button type="button" class="input-toggle"><span class="material-symbols-outlined">visibility</span></button>
              </div>
              <button type="submit" class="auth-submit-btn"><span class="material-symbols-outlined">check_circle</span> Réinitialiser</button>
            </form>
            <div class="auth-footer-text"><a class="auth-link" data-auth-target="sign-in"><span class="material-symbols-outlined" style="font-size:14px!important;vertical-align:middle;">arrow_back</span> Retour à la connexion</a></div>
          </div>
        </div>
      </div>
    </section>

    <!-- TWO-STEP VERIFICATION -->
    <section class="auth-view" id="auth-two-step" style="display:none;">
      <div class="auth-cover-layout">
        <div class="auth-cover-panel">
          <div class="auth-cover-brand">
            <div class="logo-icon"><span class="material-symbols-outlined">auto_awesome</span></div>
            <span>Prévia</span>
          </div>
          <div class="auth-cover-content">
            <div class="auth-cover-illustration">
              <span class="material-symbols-outlined">security</span>
              <div class="ring-1"></div>
              <div class="ring-2"></div>
            </div>
            <h2>Vérification<br/>en deux étapes</h2>
            <p>Pour des raisons de sécurité, veuillez saisir le code de vérification envoyé à votre adresse email.</p>
          </div>
        </div>
        <div class="auth-form-panel">
          <div class="auth-form-card">
            <div class="auth-form-header">
              <div class="auth-badge"><span class="material-symbols-outlined">security</span> 2FA</div>
              <h3>Code de vérification</h3>
              <p>Un code à 6 chiffres a été envoyé à votre adresse email. Veuillez le saisir ci-dessous.</p>
            </div>
            <form onsubmit="return false;">
              <div class="auth-code-row">
                <input type="text" class="auth-code-input" maxlength="1" placeholder="0">
                <input type="text" class="auth-code-input" maxlength="1" placeholder="0">
                <input type="text" class="auth-code-input" maxlength="1" placeholder="0">
                <input type="text" class="auth-code-input" maxlength="1" placeholder="0">
                <input type="text" class="auth-code-input" maxlength="1" placeholder="0">
                <input type="text" class="auth-code-input" maxlength="1" placeholder="0">
              </div>
              <button type="submit" class="auth-submit-btn"><span class="material-symbols-outlined">verified</span> Vérifier</button>
            </form>
            <div class="auth-footer-text" style="margin-top:16px;font-size:12px;">
              Vous n'avez pas reçu le code ? <a class="auth-link" style="font-size:12px;">Renvoyer</a>
            </div>
          </div>
        </div>
      </div>
    </section>'''

# ── Replace the old auth section ──────────────────────────────────

old_auth_marker = '    <!-- ====== AUTH ====== -->'

# Find the old auth section: from <!-- ====== AUTH ====== --> to <div class="dashboard-container">
idx = content.find(old_auth_marker)
if idx < 0:
    print('ERROR: Could not find auth marker')
    exit(1)

# Find the start of dashboard-container (the section AFTER the auth section)
dashboard_idx = content.find('<div class="dashboard-container">', idx)
if dashboard_idx < 0:
    print('ERROR: Could not find dashboard-container')
    exit(1)

# Old content to replace (from auth marker to dashboard-container)
old_auth_section = content[idx:dashboard_idx]

# Replace
new_content = content.replace(old_auth_section, AUTH_PANELS + '\n    ')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('✅ Auth panels rebuilt successfully!')
print(f'   Removed old section ({len(old_auth_section)} chars)')
print(f'   Added 5 modern panels ({len(AUTH_PANELS)} chars)')
print('   Panels: sign-in, sign-up, forgot-password, reset-password, two-step')
