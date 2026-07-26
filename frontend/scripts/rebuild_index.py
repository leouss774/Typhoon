"""
Rebuild index.html: extract <head> from current file, then generate complete dashboard body.
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the <head> section
head_match = re.search(r'<head>(.*?)</head>', content, re.DOTALL)
head_content = head_match.group(1) if head_match else content

# Build the complete new body
body = '''<!doctype html>
<html lang="fr">
  <head>{head_content.strip()}
  </head>
  <body>
    <!-- ====== LANDING PAGE ====== -->
    <section class="landing-view active" id="view-landing">
      <header class="landing-header">
        <a class="landing-brand" href="#"><span class="landing-brand-title">Prévia</span></a>
        <div class="landing-actions">
          <button class="landing-btn primary landing-cta-assureur"><span class="material-symbols-outlined" style="font-size:18px!important;">badge</span> Espace Assureur</button>
          <button class="landing-btn secondary landing-cta-assure"><span class="material-symbols-outlined" style="font-size:18px!important;">person</span> Espace Assuré</button>
        </div>
      </header>
    </section>

    <div class="dashboard-container">
      <!-- Sidebar -->
      <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
          <button class="sidebar-toggle" id="sidebarToggle" aria-label="Toggle sidebar">
            <span class="material-symbols-outlined toggle-icon">menu</span>
          </button>
          <div class="sidebar-logo">
            <div class="logo-icon"><span class="material-symbols-outlined">auto_awesome</span></div>
            <span class="sidebar-logo-text">Prévia</span>
          </div>
        </div>
        <span class="sidebar-role-badge assureur" id="sidebarRoleBadge">ESPACE ASSUREUR</span>

        <nav class="sidebar-nav">
          <!-- ASSUREUR -->
          <button class="nav-item nav-role-assureur active" data-view="overview"><span class="material-symbols-outlined">dashboard</span><span class="nav-label">Vue d\\'ensemble</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-assureur" data-view="portfolio"><span class="material-symbols-outlined">folder_open</span><span class="nav-label">Portefeuille</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-assureur" data-view="clients"><span class="material-symbols-outlined">groups</span><span class="nav-label">Clients</span><md-ripple></md-ripple></button>

          <!-- EXPERT (hidden by default) -->
          <button class="nav-item nav-role-expert" data-view="expert-missions" style="display:none;"><span class="material-symbols-outlined">assignment</span><span class="nav-label">Mes missions</span><md-ripple></md-ripple></button>

          <!-- ADMIN (hidden by default) -->
          <button class="nav-item nav-role-admin" data-view="admin-overview" style="display:none;"><span class="material-symbols-outlined">admin_panel_settings</span><span class="nav-label">Overview</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-admin" data-view="admin-clients" style="display:none;"><span class="material-symbols-outlined">groups</span><span class="nav-label">Clients</span><md-ripple></md-ripple></button>

          <!-- ASSURE (hidden by default) -->
          <button class="nav-item nav-role-assure" data-view="assure-bien" style="display:none;"><span class="material-symbols-outlined">home</span><span class="nav-label">Vue d\\'ensemble</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-assure" data-view="assure-travaux" style="display:none;"><span class="material-symbols-outlined">home_repair_service</span><span class="nav-label">Mes Travaux</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-assure" data-view="assure-engagement" style="display:none;"><span class="material-symbols-outlined">verified</span><span class="nav-label">Mon Engagement</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-assure" data-view="assure-dossier" style="display:none;"><span class="material-symbols-outlined">folder_open</span><span class="nav-label">Mon Dossier</span><md-ripple></md-ripple></button>

          <button class="nav-item nav-role-assureur" data-view="settings"><span class="material-symbols-outlined">settings</span><span class="nav-label">Paramètres</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-assure" data-view="assure-settings" style="display:none;"><span class="material-symbols-outlined">settings</span><span class="nav-label">Paramètres</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-expert" data-view="expert-settings" style="display:none;"><span class="material-symbols-outlined">settings</span><span class="nav-label">Paramètres</span><md-ripple></md-ripple></button>
          <button class="nav-item nav-role-admin" data-view="admin-settings" style="display:none;"><span class="material-symbols-outlined">settings</span><span class="nav-label">Paramètres</span><md-ripple></md-ripple></button>
        </nav>

        <div class="sidebar-bottom">
          <button class="nav-item" id="headerThemeToggle">
            <span class="material-symbols-outlined theme-icon-light">light_mode</span>
            <span class="material-symbols-outlined theme-icon-dark">dark_mode</span>
            <span class="nav-label">Thème</span><md-ripple></md-ripple>
          </button>
          <button class="nav-item role-switch-btn" id="roleSwitchBtn">
            <span class="material-symbols-outlined">swap_horiz</span>
            <span class="nav-label" id="roleSwitchText">Mode Assuré</span><md-ripple></md-ripple>
          </button>
          <button class="nav-item logout-btn" data-view="logout">
            <span class="material-symbols-outlined">logout</span>
            <span class="nav-label">Déconnexion</span><md-ripple></md-ripple>
          </button>
        </div>
      </aside>

      <!-- MAIN CONTENT -->
      <main class="main-content">
        <header class="app-header">
          <div class="header-tabs" id="headerTabs">
            <button class="tab-btn" data-tab="summary">Summary</button>
            <button class="tab-btn active" data-tab="map">Map</button>
            <button class="tab-btn" data-tab="alerts">Alerts</button>
          </div>
          <div class="header-actions" id="headerActions" style="display:flex;align-items:center;gap:8px;margin-left:auto;">
            <button class="profile-trigger" id="profileTrigger">
              <span class="material-symbols-outlined">account_circle</span>
            </button>
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
              <div class="banner-gallery">
                <img class="banner-gallery-slide" src="https://images.unsplash.com/photo-1550340499-a6c60fc8287c?w=1200&q=50" alt="" loading="lazy" />
                <img class="banner-gallery-slide" src="https://images.unsplash.com/photo-1598965402089-897ce52e8355?w=1200&q=50" alt="" loading="lazy" />
              </div>
              <div class="banner-info">
                <h1>Analyse des<br>Risques Climatiques</h1>
                <p>Évaluez et gérez les risques climatiques de votre portefeuille immobilier.</p>
              </div>
              <div class="banner-completion-card">
                <div class="completion-header">
                  <div><span class="completion-label">Score de risque global</span><h2>—</h2></div>
                </div>
                <div class="completion-footer">
                  <div class="footer-stat"><span class="footer-stat-label">— évalués</span></div>
                  <div class="footer-stat align-right"><span class="footer-stat-label">— total</span></div>
                </div>
              </div>
            </div>
          </section>
          <section class="widgets-grid">
            <div class="grid-column col-span-2">
              <div class="dashboard-card cross-section-card">
                <div class="card-header"><h3>Répartition des risques</h3></div>
                <div class="card-body"><div class="card-metric"><h2>—</h2></div></div>
              </div>
            </div>
            <div class="grid-column col-span-3">
              <div class="circular-cards-row">
                <div class="dashboard-card circ-widget"><div class="widget-header"><h3>Risque inondation</h3></div><div class="circ-body"><span class="circ-pct">—</span></div></div>
                <div class="dashboard-card circ-widget"><div class="widget-header"><h3>Retrait argile</h3></div><div class="circ-body"><span class="circ-pct">—</span></div></div>
                <div class="dashboard-card circ-widget"><div class="widget-header"><h3>Risque sismique</h3></div><div class="circ-body"><span class="circ-pct">—</span></div></div>
              </div>
            </div>
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
                    <svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="48" fill="none" stroke="#f1f5f9" stroke-width="18"/><circle cx="60" cy="60" r="48" fill="none" stroke="#ef4444" stroke-width="18" stroke-dasharray="75.4" stroke-dashoffset="50.3"/></svg>
                    <div class="portfolio-dist-center"><span class="portfolio-dist-pct">—</span><span class="portfolio-dist-unit">total</span></div>
                  </div>
                  <div class="portfolio-dist-legend">
                    <div class="portfolio-dist-item"><span class="portfolio-dist-dot" style="background:#ef4444;"></span><span>Haut risque</span><span class="portfolio-dist-count">0</span></div>
                    <div class="portfolio-dist-item"><span class="portfolio-dist-dot" style="background:#f59e0b;"></span><span>Risque moyen</span><span class="portfolio-dist-count">0</span></div>
                    <div class="portfolio-dist-item"><span class="portfolio-dist-dot" style="background:#10b981;"></span><span>Faible risque</span><span class="portfolio-dist-count">0</span></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="portfolio-tab-content" data-content="map"><div class="portfolio-map-full" id="portfolioMapContainer"></div></div>
          <div class="portfolio-tab-content" data-content="trends"><div class="portfolio-trends"><div class="trend-chart-card"><div class="trend-chart-header"><div><span class="trend-chart-title">Évolution des scores</span></div></div></div></div></div>
        </section>

        <!-- PROPERTY RISK -->
        <section class="view-panel" id="view-property-risk">
          <div class="risk-steps" id="riskStepsBar">
            <button class="risk-nav-btn-prev" id="riskNavPrev"><span class="material-symbols-outlined">chevron_left</span></button>
            <div class="risk-step active" data-step="locate"><span class="risk-step-circle">1</span><div class="risk-step-text"><span class="risk-step-name">Locate</span><span class="risk-step-desc">Chercher un bien</span></div></div>
            <div class="risk-step-line"></div>
            <div class="risk-step" data-step="actuariat"><span class="risk-step-circle">2</span><div class="risk-step-text"><span class="risk-step-name">Actuariat</span><span class="risk-step-desc">Questionnaire technique</span></div></div>
            <div class="risk-step-line"></div>
            <div class="risk-step" data-step="inspect"><span class="risk-step-circle">3</span><div class="risk-step-text"><span class="risk-step-name">Inspect</span><span class="risk-step-desc">Analyser les composants 3D</span></div></div>
            <div class="risk-step-line"></div>
            <div class="risk-step" data-step="evaluate"><span class="risk-step-circle">4</span><div class="risk-step-text"><span class="risk-step-name">Evaluate</span><span class="risk-step-desc">Score + avenant</span></div></div>
            <button class="risk-nav-btn-next" id="riskNavNext"><span class="material-symbols-outlined">chevron_right</span></button>
          </div>
          <div class="risk-tab-content active" data-content="locate">
            <div class="bdnb-search-bar"><div class="bdnb-search-input-group"><span class="material-symbols-outlined bdnb-search-icon">search</span><input type="text" id="bdnbSearchInput" class="bdnb-search-input" placeholder="Rechercher une adresse..." /><button class="bdnb-search-btn" id="bdnbSearchBtn"><span class="material-symbols-outlined">travel_explore</span> Rechercher</button></div></div>
            <div class="risk-locate-layout"><div class="risk-locate-map" id="riskLocateMap"><div id="climateMapContainer" style="width:100%;height:100%;min-height:400px;"></div></div><div class="risk-locate-panel" id="riskLocatePanel"><div class="rp-container" id="riskResultsPanel"><div class="rp-empty-state"><span class="material-symbols-outlined" style="font-size:40px;color:var(--text-muted);opacity:0.3;">gps_fixed</span><p style="font-size:12px;color:var(--text-muted);">Recherchez une adresse</p></div></div></div></div>
          </div>
          <div class="risk-tab-content" data-content="actuariat"><div class="risk-expert-layout"><div class="risk-expert-main"><p style="padding:20px;color:var(--text-muted);">Contenu actuariat</p></div><div class="risk-expert-side"><div class="risk-expert-card"><h4><span class="material-symbols-outlined" style="font-size:16px!important;">calculate</span> Résumé</h4><div class="risk-expert-summary" id="riskExpertFormSummary"><div class="risk-expert-summary-row"><span>Champs</span><span class="risk-expert-summary-val">0 / 15</span></div></div></div><button class="risk-expert-action-btn" id="riskExpertCalcBtn"><span class="material-symbols-outlined">calculate</span> Calculer ▶</button></div></div></div>
          <div class="risk-tab-content" data-content="inspect">
            <div class="risk-inspect-layout"><div class="risk-inspect-3d"><div id="riskHouseContainer" class="house-3d-container"></div></div><div class="risk-inspect-panel"><div class="risk-inspect-card" id="riskInspectInfo"><h4><span class="material-symbols-outlined">touch_app</span> Composant</h4></div></div></div>
            <div class="risk-inspect-card risk-inspect-card-full"><h4>Composants du bâtiment</h4><div class="risk-inspect-components" id="riskComponentGrid"></div></div>
          </div>
          <div class="risk-tab-content" data-content="evaluate">
            <div class="risk-evaluate-layout"><div class="risk-evaluate-main"><div class="risk-pricing-signal" id="riskPricingSignal"><span class="risk-pricing-signal-label" id="riskSignalLabel">STANDARD</span></div><div class="risk-eval-section" id="riskContributorsSection"><h4>Décomposition des scores</h4><div class="risk-contributors-grid" id="riskContributorsGrid"><div class="rp-empty">Lancez l\\'évaluation</div></div></div><div class="risk-eval-section" id="riskAINarrativeSection"><h4>Analyse IA</h4><div class="risk-ai-narrative" id="riskAiNarrative"></div></div></div><div class="risk-evaluate-side"><div class="risk-eval-card"><h4>Avenant</h4></div></div></div>
          </div>
        </section>

        <!-- CLIENTS -->
        <section class="view-panel" id="view-clients">
          <div class="clients-tab-content active" data-content="info">
            <div class="clients-header">
              <div><h3>Clients</h3><p>Gestion des clients et des polices</p></div>
              <div class="clients-header-actions">
                <div class="clients-search-box"><span class="material-symbols-outlined clients-search-icon">search</span><input type="text" class="clients-search-input" id="clientsSearch" placeholder="Rechercher un client..." /></div>
                <button class="clients-add-btn" id="clientsAddBtn"><span class="material-symbols-outlined" style="font-size:16px!important;">add</span> Nouveau client</button>
              </div>
            </div>
            <div class="clients-stats-row">
              <div class="clients-stat-card"><span class="clients-stat-value">—</span><span class="clients-stat-label">Total clients</span></div>
              <div class="clients-stat-card"><span class="clients-stat-value">—</span><span class="clients-stat-label">Contrats actifs</span></div>
              <div class="clients-stat-card"><span class="clients-stat-value">—</span><span class="clients-stat-label">En attente</span></div>
            </div>
            <div class="clients-table-container">
              <table class="clients-table">
                <thead><tr><th></th><th>Civilité</th><th>Nom</th><th>Email</th><th>Téléphone</th><th>Ville</th><th>Statut</th><th></th></tr></thead>
                <tbody id="clientsTableBody"></tbody>
              </table>
            </div>
          </div>
          <div class="clients-detail-panel" id="clientsDetailPanel">
            <div class="cdp-back-row"><button class="cdp-back-btn" id="cdpBackBtn"><span class="material-symbols-outlined">arrow_back</span> Retour</button></div>
            <div class="cdp-profile"><div class="cdp-avatar" id="cdpAvatar">JD</div><div><h2 id="cdpName">Client</h2><span class="cdp-status" id="cdpStatus">Actif</span></div></div>
            <div class="cdp-tabs">
              <button class="cdp-tab active" data-cdp-tab="overview">Aperçu</button>
              <button class="cdp-tab" data-cdp-tab="info">Infos</button>
              <button class="cdp-tab" data-cdp-tab="contrats">Contrats</button>
              <button class="cdp-tab" data-cdp-tab="paiements">Paiements</button>
            </div>
            <div class="cdp-tab-content active" data-cdp-content="overview"><div id="cdpContractsList"></div></div>
            <div class="cdp-tab-content" data-cdp-content="info"><p style="padding:16px;color:var(--text-muted);font-size:12px;">Infos détaillées</p></div>
            <div class="cdp-tab-content" data-cdp-content="contrats"><p style="padding:16px;color:var(--text-muted);font-size:12px;">Contrats</p></div>
            <div class="cdp-tab-content" data-cdp-content="paiements"><p style="padding:16px;color:var(--text-muted);font-size:12px;">Paiements</p></div>
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
        <section class="view-panel" id="view-assure-bien"><div class="assure-dashboard-card"><p style="padding:20px;color:var(--text-muted);">Mon Bien - formulaire</p></div></section>
        <section class="view-panel" id="view-assure-travaux"><div class="assure-travaux-layout"><h3>Mes Travaux</h3></div></section>
        <section class="view-panel" id="view-assure-engagement"><div class="assure-engagement-layout"><h3>Mon Engagement</h3></div></section>
        <section class="view-panel" id="view-assure-dossier"><div class="assure-dossier-layout"><h3>Mon Dossier</h3></div></section>
      </main>
    </div>

    <script type="module" src="/src/main.ts"></script>
  </body>
</html>'''

# Write the file
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(body)

print("✅ index.html rebuilt with all view panels")
