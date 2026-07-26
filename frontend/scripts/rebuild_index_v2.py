"""
Complete rebuild of index.html with all dashboard view panels and sub-views.
Generates the full HTML including admin, expert, auth views, clients detail, and actuarial form.
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

head_match = re.search(r'<head>(.*?)</head>', content, re.DOTALL)
head_content = head_match.group(1) if head_match else ''

# Generate the complete body
body = f'''<!doctype html>
<html lang="fr">
  <head>{head_content.strip()}
  </head>
  <body>
    <!-- ====== LANDING ====== -->
    <section class="landing-view active" id="view-landing">
      <header class="landing-header">
        <a class="landing-brand" href="#"><span class="landing-brand-title">Prévia</span></a>
        <div class="landing-actions">
          <button class="landing-btn primary landing-cta-assureur"><span class="material-symbols-outlined" style="font-size:18px!important;">badge</span> Espace Assureur</button>
          <button class="landing-btn secondary landing-cta-assure"><span class="material-symbols-outlined" style="font-size:18px!important;">person</span> Espace Assuré</button>
        </div>
      </header>
    </section>

    <!-- ====== AUTH ====== -->
    <section class="auth-view" id="view-auth-sign-in" style="display:none;">
      <div class="auth-container">
        <div class="auth-card">
          <h2>Connexion</h2>
          <form id="authForm">
            <input type="email" id="authEmail" placeholder="Email" required />
            <input type="password" id="authPassword" placeholder="Mot de passe" required />
            <button type="submit" id="authSubmitBtn">Se connecter</button>
          </form>
          <p><a href="#" id="authSwitchLink">Créer un compte</a></p>
        </div>
      </div>
    </section>

    <div class="dashboard-container">
      <!-- SIDEBAR -->
      <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
          <button class="sidebar-toggle" id="sidebarToggle"><span class="material-symbols-outlined toggle-icon">menu</span></button>
          <div class="sidebar-logo"><div class="logo-icon"><span class="material-symbols-outlined">auto_awesome</span></div><span class="sidebar-logo-text">Prévia</span></div>
        </div>
        <span class="sidebar-role-badge assureur" id="sidebarRoleBadge">ESPACE ASSUREUR</span>
        <nav class="sidebar-nav">
          <button class="nav-item nav-role-assureur active" data-view="overview"><span class="material-symbols-outlined">dashboard</span><span class="nav-label">Vue d\'ensemble</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-assureur" data-view="portfolio"><span class="material-symbols-outlined">folder_open</span><span class="nav-label">Portefeuille</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-assureur" data-view="clients"><span class="material-symbols-outlined">groups</span><span class="nav-label">Clients</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-assureur" data-view="settings"><span class="material-symbols-outlined">settings</span><span class="nav-label">Paramètres</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-assure" data-view="assure-bien" style="display:none;"><span class="material-symbols-outlined">home</span><span class="nav-label">Vue d\'ensemble</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-assure" data-view="assure-travaux" style="display:none;"><span class="material-symbols-outlined">home_repair_service</span><span class="nav-label">Mes Travaux</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-assure" data-view="assure-engagement" style="display:none;"><span class="material-symbols-outlined">verified</span><span class="nav-label">Mon Engagement</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-assure" data-view="assure-dossier" style="display:none;"><span class="material-symbols-outlined">folder_open</span><span class="nav-label">Mon Dossier</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-assure" data-view="assure-settings" style="display:none;"><span class="material-symbols-outlined">settings</span><span class="nav-label">Paramètres</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-expert" data-view="expert-missions" style="display:none;"><span class="material-symbols-outlined">assignment</span><span class="nav-label">Missions</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-expert" data-view="expert-settings" style="display:none;"><span class="material-symbols-outlined">settings</span><span class="nav-label">Paramètres</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-admin" data-view="admin-overview" style="display:none;"><span class="material-symbols-outlined">admin_panel_settings</span><span class="nav-label">Overview</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-admin" data-view="admin-clients" style="display:none;"><span class="material-symbols-outlined">groups</span><span class="nav-label">Clients</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-admin" data-view="admin-settings" style="display:none;"><span class="material-symbols-outlined">settings</span><span class="nav-label">Paramètres</span><md-ripple></md-ripple></button>
        </nav>
        <div class="sidebar-bottom">
          <button class="nav-item" id="headerThemeToggle"><span class="material-symbols-outlined theme-icon-light">light_mode</span><span class="material-symbols-outlined theme-icon-dark">dark_mode</span><span class="nav-label">Thème</span><md-ripple></md-ripple></button>
          <button class="nav-item role-switch-btn" id="roleSwitchBtn"><span class="material-symbols-outlined">swap_horiz</span><span class="nav-label" id="roleSwitchText">Mode Assuré</span><md-ripple></md-ripple></button>
          <button class="nav-item logout-btn" data-view="logout"><span class="material-symbols-outlined">logout</span><span class="nav-label">Déconnexion</span><md-ripple></md-ripple></button>
        </div>
      </aside>

      <!-- MAIN -->
      <main class="main-content">
        <header class="app-header">
          <div class="header-tabs" id="headerTabs"></div>
          <div class="header-actions" id="headerActions" style="display:flex;align-items:center;gap:8px;margin-left:auto;">
            <button class="profile-trigger" id="profileTrigger"><span class="material-symbols-outlined">account_circle</span></button>
            <div class="profile-menu" id="profileMenu">
              <div class="profile-menu-item" data-action="profile">Profil</div>
              <div class="profile-menu-item" data-action="settings">Paramètres</div>
              <div class="profile-menu-item" data-action="logout">Déconnexion</div>
            </div>
          </div>
        </header>

        <!-- OVERVIEW -->
        <section class="view-panel active" id="view-overview">
          <section class="banner-section">
            <div class="banner-card">
              <div class="banner-info">
                <h1>Analyse des Risques Climatiques</h1>
                <p>Évaluez et gérez les risques climatiques de votre portefeuille immobilier.</p>
              </div>
              <div class="banner-completion-card">
                <div class="completion-header"><div><span class="completion-label">Score</span><h2>—</h2></div></div>
                <div class="completion-footer"><span class="footer-stat-label">0 évalués</span><span class="footer-stat-label">0 total</span></div>
              </div>
            </div>
          </section>
          <section class="widgets-grid">
            <div class="grid-column col-span-2"><div class="dashboard-card"><div class="card-header"><h3>Répartition des risques</h3></div></div></div>
            <div class="grid-column col-span-3"><div class="circular-cards-row"><div class="dashboard-card circ-widget"><h3>Risque</h3><span class="circ-pct">—</span></div></div></div>
          </section>
        </section>

        <!-- PORTFOLIO -->
        <section class="view-panel" id="view-portfolio">
          <div class="portfolio-tab-content active" data-content="summary">
            <div class="portfolio-kpi-row" id="portfolioKpiRow">
              <div class="portfolio-kpi"><span class="material-symbols-outlined" style="color:var(--color-primary);">home</span><div><span class="portfolio-kpi-value" id="portKpiProperties">—</span><span class="portfolio-kpi-label">Propriétés</span></div></div>
              <div class="portfolio-kpi"><span class="material-symbols-outlined" style="color:#ef4444;">warning</span><div><span class="portfolio-kpi-value" id="portKpiHighRisk">—</span><span class="portfolio-kpi-label">Haut risque</span></div></div>
              <div class="portfolio-kpi"><span class="material-symbols-outlined" style="color:#f59e0b;">speed</span><div><span class="portfolio-kpi-value" id="portKpiAvgScore">—</span><span class="portfolio-kpi-label">Score moyen</span></div></div>
              <div class="portfolio-kpi"><span class="material-symbols-outlined" style="color:#10b981;">euro</span><div><span class="portfolio-kpi-value" id="portKpiImpact">—</span><span class="portfolio-kpi-label">Impact</span></div></div>
              <div class="portfolio-kpi"><span class="material-symbols-outlined" style="color:#3b82f6;">account_balance</span><div><span class="portfolio-kpi-value" id="portKpiCities">—</span><span class="portfolio-kpi-label">Villes</span></div></div>
            </div>
            <div class="portfolio-split">
              <div class="portfolio-grid" id="portfolioGrid"></div>
              <div class="portfolio-dist-card">
                <div class="card-header"><h3>Répartition des risques</h3></div>
                <div class="portfolio-dist-chart">
                  <div class="portfolio-dist-ring">
                    <svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="48" fill="none" stroke="#f1f5f9" stroke-width="18"/></svg>
                    <div class="portfolio-dist-center"><span class="portfolio-dist-pct">—</span><span class="portfolio-dist-unit">total</span></div>
                  </div>
                  <div class="portfolio-dist-legend">
                    <div class="portfolio-dist-item"><span class="portfolio-dist-dot" style="background:#ef4444;"></span><span>Haut risque</span><span class="portfolio-dist-count">0</span></div>
                    <div class="portfolio-dist-item"><span class="portfolio-dist-dot" style="background:#f59e0b;"></span><span>Moyen</span><span class="portfolio-dist-count">0</span></div>
                    <div class="portfolio-dist-item"><span class="portfolio-dist-dot" style="background:#10b981;"></span><span>Faible</span><span class="portfolio-dist-count">0</span></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="portfolio-tab-content" data-content="map"><div class="portfolio-map-full" id="portfolioMapContainer"></div></div>
          <div class="portfolio-tab-content" data-content="trends"><div class="portfolio-trends"><div class="trend-chart-card"><div class="trend-chart-header"><h3>Évolution</h3></div></div></div></div>
        </section>

        <!-- PROPERTY RISK -->
        <section class="view-panel" id="view-property-risk">
          <div class="risk-steps" id="riskStepsBar">
            <button class="risk-nav-btn-prev" id="riskNavPrev"><span class="material-symbols-outlined">chevron_left</span></button>
            <div class="risk-step active" data-step="locate"><span class="risk-step-circle">1</span><div class="risk-step-text"><span class="risk-step-name">Locate</span><span class="risk-step-desc">Chercher un bien</span></div></div>
            <div class="risk-step-line"></div>
            <div class="risk-step" data-step="actuariat"><span class="risk-step-circle">2</span><div class="risk-step-text"><span class="risk-step-name">Actuariat</span><span class="risk-step-desc">Questionnaire technique</span></div></div>
            <div class="risk-step-line"></div>
            <div class="risk-step" data-step="inspect"><span class="risk-step-circle">3</span><div class="risk-step-text"><span class="risk-step-name">Inspect</span><span class="risk-step-desc">Analyser les composants</span></div></div>
            <div class="risk-step-line"></div>
            <div class="risk-step" data-step="evaluate"><span class="risk-step-circle">4</span><div class="risk-step-text"><span class="risk-step-name">Evaluate</span><span class="risk-step-desc">Score + avenant</span></div></div>
            <button class="risk-nav-btn-next" id="riskNavNext"><span class="material-symbols-outlined">chevron_right</span></button>
          </div>
          <!-- Locate -->
          <div class="risk-tab-content active" data-content="locate">
            <div class="bdnb-search-bar"><div class="bdnb-search-input-group"><span class="material-symbols-outlined bdnb-search-icon">search</span><input type="text" id="bdnbSearchInput" class="bdnb-search-input" placeholder="Rechercher une adresse..." /><button class="bdnb-search-btn" id="bdnbSearchBtn"><span class="material-symbols-outlined">travel_explore</span> Rechercher</button></div></div>
            <div class="risk-locate-layout"><div class="risk-locate-map" id="riskLocateMap"><div id="climateMapContainer" style="width:100%;height:100%;min-height:400px;"></div></div><div class="risk-locate-panel" id="riskLocatePanel"><div class="rp-container" id="riskResultsPanel"><div class="rp-empty-state"><span class="material-symbols-outlined" style="font-size:40px;">gps_fixed</span><p>Recherchez une adresse</p></div></div></div></div>
          </div>
          <!-- Actuariat -->
          <div class="risk-tab-content" data-content="actuariat">
            <div class="risk-expert-layout">
              <div class="risk-expert-main">
                <div class="risk-expert-form-banner" id="riskExpertFormBanner"><h3>Questionnaire technique</h3></div>
                <div class="risk-expert-form">
                  <details class="risk-expert-accordion" open>
                    <summary class="risk-expert-accordion-header"><span class="material-symbols-outlined">home</span><span>Général</span></summary>
                    <div class="risk-expert-accordion-body">
                      <div class="risk-expert-form-grid">
                        <div class="risk-expert-form-field"><label>Type de bien</label><select id="expertTypeBien" class="risk-expert-select"><option value="individuelle">Maison individuelle</option><option value="mitoyenne">Maison mitoyenne</option><option value="appartement">Appartement</option></select></div>
                        <div class="risk-expert-form-field"><label>Nb pièces</label><input type="number" id="expertNbPieces" class="risk-expert-input" value="5" /></div>
                        <div class="risk-expert-form-field"><label>Sous-sol</label><select id="expertSousSol" class="risk-expert-select"><option value="non">Non</option><option value="oui">Oui</option></select></div>
                        <div class="risk-expert-form-field"><label>Capital assuré (€)</label><input type="number" id="expertCapitalAssure" class="risk-expert-input" value="250000" /></div>
                      </div>
                    </div>
                  </details>
                  <details class="risk-expert-accordion" open>
                    <summary class="risk-expert-accordion-header"><span class="material-symbols-outlined">water_flood</span><span>Inondation</span></summary>
                    <div class="risk-expert-accordion-body">
                      <div class="risk-expert-form-grid">
                        <div class="risk-expert-form-field"><label>Hauteur plancher (cm)</label><input type="number" id="expertHauteurPlancher" class="risk-expert-input" value="30" /></div>
                        <div class="risk-expert-form-field"><label>Clapet anti-retour</label><select id="expertClapet" class="risk-expert-select"><option value="non">Non</option><option value="oui">Oui</option></select></div>
                        <div class="risk-expert-form-field"><label>Équipements électriques sous-sol</label><select id="expertEquipElec" class="risk-expert-select"><option value="non">Non</option><option value="oui">Oui</option></select></div>
                        <div class="risk-expert-form-field"><label>Zone inondable</label><select id="expertZoneInondable" class="risk-expert-select"><option value="none">Non concerné</option><option value="faible">Faible</option><option value="moyen">Moyen</option><option value="fort">Fort</option></select></div>
                      </div>
                    </div>
                  </details>
                  <details class="risk-expert-accordion" open>
                    <summary class="risk-expert-accordion-header"><span class="material-symbols-outlined">landslide</span><span>RGA / Argile</span></summary>
                    <div class="risk-expert-accordion-body">
                      <div class="risk-expert-form-grid">
                        <div class="risk-expert-form-field"><label>Profondeur fondations</label><select id="expertProfFondations" class="risk-expert-select"><option value="moins50">&lt;50 cm</option><option value="50a80">50-80 cm</option><option value="plus80">&gt;80 cm</option></select></div>
                        <div class="risk-expert-form-field"><label>Fissures</label><select id="expertFissures" class="risk-expert-select"><option value="aucune">Aucune</option><option value="legeres">Légères</option><option value="importantes">Importantes</option></select></div>
                        <div class="risk-expert-form-field"><label>Arbres &lt;5m</label><select id="expertArbres" class="risk-expert-select"><option value="non">Non</option><option value="oui">Oui</option></select></div>
                        <div class="risk-expert-form-field"><label>Cave</label><select id="expertCave" class="risk-expert-select"><option value="non">Non</option><option value="oui">Oui</option></select></div>
                      </div>
                    </div>
                  </details>
                  <details class="risk-expert-accordion" open>
                    <summary class="risk-expert-accordion-header"><span class="material-symbols-outlined">air</span><span>Tempête & Toiture</span></summary>
                    <div class="risk-expert-accordion-body">
                      <div class="risk-expert-form-grid">
                        <div class="risk-expert-form-field"><label>Âge toiture (ans)</label><input type="number" id="expertAgeToiture" class="risk-expert-input" value="15" /></div>
                        <div class="risk-expert-form-field"><label>Matériau toit</label><select id="expertMateriauToit" class="risk-expert-select"><option value="tuiles">Tuiles</option><option value="ardoises">Ardoises</option><option value="tole">Bac acier</option></select></div>
                        <div class="risk-expert-form-field"><label>Panneaux solaires</label><select id="expertPanneauxSolaires" class="risk-expert-select"><option value="non">Non</option><option value="oui">Oui</option></select></div>
                      </div>
                    </div>
                  </details>
                </div>
              </div>
              <div class="risk-expert-side">
                <div class="risk-expert-card"><h4><span class="material-symbols-outlined" style="font-size:16px!important;">calculate</span> Résumé</h4><div class="risk-expert-summary" id="riskExpertFormSummary"><div class="risk-expert-summary-row"><span>Champs</span><span class="risk-expert-summary-val">0 / 15</span></div><div class="risk-expert-summary-row"><span>Adresse</span><span class="risk-expert-summary-val" id="riskExpertFormAddr">—</span></div></div></div>
                <button class="risk-expert-action-btn" id="riskExpertCalcBtn" style="width:100%;"><span class="material-symbols-outlined">calculate</span> Calculer ▶</button>
              </div>
            </div>
          </div>
          <!-- Inspect -->
          <div class="risk-tab-content" data-content="inspect">
            <div class="risk-inspect-header">
              <div id="riskMergedScore"><div class="risk-merged-score-display"><div class="risk-merged-score-ring"><span class="risk-merged-score-val">—</span></div></div></div>
              <div class="risk-time-toggle" id="riskTimeToggle">
                <button class="risk-time-toggle-btn active" data-mode="current"><span class="material-symbols-outlined">today</span> État actuel</button>
                <button class="risk-time-toggle-btn" data-mode="projected"><span class="material-symbols-outlined">air</span> Projection 2050</button>
              </div>
            </div>
            <div class="risk-inspect-layout"><div class="risk-inspect-3d"><div id="riskHouseContainer" class="house-3d-container"></div></div><div class="risk-inspect-panel"><div class="risk-inspect-card" id="riskInspectInfo"><h4>Composant</h4></div></div></div>
            <div class="risk-inspect-card risk-inspect-card-full"><h4>Composants du bâtiment</h4><div class="risk-inspect-components" id="riskComponentGrid"></div></div>
          </div>
          <!-- Evaluate -->
          <div class="risk-tab-content" data-content="evaluate">
            <div class="risk-evaluate-layout">
              <div class="risk-evaluate-main">
                <div class="risk-pricing-signal" id="riskPricingSignal"><span class="risk-pricing-signal-label" id="riskSignalLabel">STANDARD</span><span class="risk-pricing-signal-sub">Score: —</span></div>
                <div class="risk-score-row evaluate-score-row">
                  <div class="risk-score-card"><span>Actuel</span><span class="risk-score-gauge-val" id="riskGaugeValCurrent">—</span><span class="risk-badge" id="riskBadgeCurrent">—</span></div>
                  <div class="risk-score-card"><span>Projeté</span><span class="risk-score-gauge-val" id="riskGaugeValProjected">—</span><span class="risk-badge" id="riskBadgeProjected">—</span></div>
                  <div class="risk-score-improve"><span>Amélioration</span><span id="riskImproveVal">—</span></div>
                </div>
                <div class="risk-eval-section" id="riskContributorsSection"><h4>Décomposition</h4><div class="risk-contributors-grid" id="riskContributorsGrid"><div class="rp-empty">Lancez l\'évaluation</div></div></div>
                <div class="risk-eval-section" id="riskAINarrativeSection"><h4>Analyse IA</h4><div class="risk-ai-narrative" id="riskAiNarrative"><p class="risk-ai-placeholder">Cliquez sur Calculer</p></div></div>
              </div>
              <div class="risk-evaluate-side">
                <div class="risk-eval-card"><h4>Avenant</h4>
                  <div class="risk-uw-row"><span>Override</span><select class="risk-uw-select" id="riskUwScoreOverride"><option value="">Aucun</option></select></div>
                  <div class="risk-uw-row"><span>Justification</span><textarea class="risk-uw-textarea" id="riskUwRationale"></textarea></div>
                  <div class="risk-uw-status-row">
                    <button class="risk-uw-btn favorable" data-signal="FAVORABLE">Favorable</button>
                    <button class="risk-uw-btn standard active" data-signal="STANDARD">Standard</button>
                    <button class="risk-uw-btn surcharge" data-signal="SURCHARGE">Surcharge</button>
                    <button class="risk-uw-btn decline" data-signal="DECLINER">Décliner</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- CLIENTS -->
        <section class="view-panel" id="view-clients">
          <div class="clients-tab-content active" data-content="info">
            <div class="clients-header">
              <div><h3>Clients</h3></div>
              <div class="clients-header-actions">
                <div class="clients-search-box"><span class="material-symbols-outlined clients-search-icon">search</span><input type="text" class="clients-search-input" id="clientsSearch" placeholder="Rechercher..." /></div>
                <button class="clients-add-btn" id="clientsAddBtn"><span class="material-symbols-outlined" style="font-size:16px!important;">add</span> Nouveau client</button>
              </div>
            </div>
            <div class="clients-table-container">
              <table class="clients-table"><thead><tr><th></th><th>Nom</th><th>Email</th><th>Téléphone</th><th>Ville</th><th>Statut</th><th></th></tr></thead><tbody id="clientsTableBody"></tbody></table>
            </div>
          </div>
          <!-- Client Detail Panel -->
          <div class="clients-detail-panel" id="clientsDetailPanel">
            <div class="cdp-back-row"><button class="cdp-back-btn" id="cdpBackBtn"><span class="material-symbols-outlined">arrow_back</span> Retour</button></div>
            <div class="cdp-profile"><div class="cdp-avatar" id="cdpAvatar">JD</div><div><h2 id="cdpName">Client</h2><span class="cdp-status" id="cdpStatus">Actif</span></div>
              <div class="cdp-profile-actions">
                <button class="cdp-btn cdp-btn-outline" id="cdpEditToggle"><span class="material-symbols-outlined" style="font-size:16px!important;">edit</span> Modifier</button>
                <button class="cdp-btn cdp-btn-primary" id="cdpEvaluateBtn"><span class="material-symbols-outlined" style="font-size:16px!important;">gps_fixed</span> Évaluer ce bien</button>
              </div>
            </div>
            <div class="cdp-tabs">
              <button class="cdp-tab active" data-cdp-tab="overview">Aperçu</button>
              <button class="cdp-tab" data-cdp-tab="contrats">Contrats</button>
            </div>
            <div class="cdp-tab-content active" data-cdp-content="overview"><div id="cdpContractsList"><p style="padding:16px;color:var(--text-muted);">Aucun bien</p></div></div>
            <div class="cdp-tab-content" data-cdp-content="contrats"><p style="padding:16px;color:var(--text-muted);">Contrats</p></div>
          </div>
          <!-- Client Wizard Modal -->
          <div class="modal-overlay" id="clientWizardModal" style="display:none;">
            <div class="modal-content">
              <button class="modal-close" id="wizardClose"><span class="material-symbols-outlined">close</span></button>
              <h3>Nouveau client</h3>
              <form id="clientWizardForm">
                <input type="text" id="wiz-firstname" placeholder="Prénom" required />
                <input type="text" id="wiz-lastname" placeholder="Nom" required />
                <input type="email" id="wiz-email" placeholder="Email" />
                <input type="tel" id="wiz-phone" placeholder="Téléphone" />
                <input type="text" id="wiz-address" placeholder="Adresse" />
                <input type="text" id="wiz-cp" placeholder="Code postal" />
                <input type="text" id="wiz-city" placeholder="Ville" />
                <button type="submit" id="wizardSubmit">Créer le client</button>
              </form>
            </div>
          </div>
        </section>

        <!-- SETTINGS -->
        <section class="view-panel" id="view-settings">
          <div class="settings-tab-content active" data-content="account"><div class="settings-section"><h3>Compte</h3></div></div>
          <div class="settings-tab-content" data-content="security"><div class="settings-section"><h3>Sécurité</h3></div></div>
          <div class="settings-tab-content" data-content="billing"><div class="settings-section"><h3>Facturation</h3></div></div>
          <div class="settings-tab-content" data-content="notifications"><div class="settings-section"><h3>Notifications</h3></div></div>
          <div class="settings-tab-content" data-content="connections"><div class="settings-section"><h3>Connexions</h3></div></div>
        </section>

        <!-- ASSURE VIEWS -->
        <section class="view-panel" id="view-assure-bien"><div class="assure-dashboard-card"><h3>Mon Bien</h3></div></section>
        <section class="view-panel" id="view-assure-travaux"><div class="assure-travaux-layout"><h3>Mes Travaux</h3><div id="assureCompGrid"></div></div></section>
        <section class="view-panel" id="view-assure-engagement"><div class="assure-engagement-layout"><h3>Mon Engagement</h3></div></section>
        <section class="view-panel" id="view-assure-dossier"><div class="assure-dossier-layout"><h3>Mon Dossier</h3></div></section>

        <!-- ADMIN VIEWS -->
        <section class="view-panel" id="view-admin-overview"><div class="admin-layout"><h3>Admin Overview</h3></div></section>
        <section class="view-panel" id="view-admin-clients"><div class="admin-layout"><h3>Admin Clients</h3></div></section>
        <section class="view-panel" id="view-admin-settings"><div class="admin-layout"><h3>Admin Settings</h3></div></section>

        <!-- EXPERT VIEWS -->
        <section class="view-panel" id="view-expert-missions"><div class="expert-layout"><h3>Mes Missions</h3></div></section>
        <section class="view-panel" id="view-expert-settings"><div class="expert-layout"><h3>Expert Settings</h3></div></section>
      </main>
    </div>

    <script type="module" src="/src/main.ts"></script>
  </body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(body)

import re
ids = re.findall(r'id="(view-[^"]*)"', body)
print("View panels generated:")
for v in ids:
    print(f"  {v}")
