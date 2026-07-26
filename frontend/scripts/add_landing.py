"""Add the landing page HTML to index.html, right after <body>."""
import os; script_dir = os.path.dirname(os.path.abspath(__file__)); project_root = os.path.join(script_dir, '..')
with open(os.path.join(project_root, 'index.html'), 'r', encoding='utf-8') as f:
    content = f.read()

landing_html = """<!-- ====== LANDING PAGE ====== -->
<section class="landing-view active" id="view-landing">
  <!-- Header -->
  <header class="landing-header">
    <a class="landing-brand" href="#">
      <div class="landing-brand-icon"><span class="material-symbols-outlined">auto_awesome</span></div>
      <span class="landing-brand-title">Prévia</span>
    </a>
    <nav class="landing-nav">
      <a class="landing-nav-link" href="#portails">Portails</a>
      <a class="landing-nav-link" href="#fonctionnalites">Fonctionnalités</a>
      <a class="landing-nav-link" href="#apropos">À propos</a>
      <a class="landing-nav-link" data-auth-target="sign-in">Connexion</a>
    </nav>
    <div class="landing-actions">
      <button class="landing-btn primary landing-cta-assureur" style="background:#6366f1;box-shadow:0 4px 14px rgba(99,102,241,0.35);">
        <span class="material-symbols-outlined" style="font-size:18px!important;">badge</span>
        Espace Assureur
      </button>
      <button class="landing-btn accent landing-cta-assure">
        <span class="material-symbols-outlined" style="font-size:18px!important;">person</span>
        Espace Assuré
      </button>
    </div>
  </header>

  <!-- Hero -->
  <section class="landing-hero">
    <div class="landing-badge">
      <span class="material-symbols-outlined" style="font-size:16px!important;">psychology</span>
      Évaluation des Risques Climatiques
    </div>
    <h1>
      Anticipez les risques climatiques<br>
      <span class="gradient-text">avec une précision inégalée</span>
    </h1>
    <p class="subtitle">
      Prévia combine données géospatiales, intelligence artificielle et expertise actuarielle
      pour évaluer, prévenir et gérer les risques climatiques de vos biens assurés.
    </p>
    <div class="landing-hero-ctas">
      <button class="landing-btn primary landing-cta-assureur" style="background:#6366f1;box-shadow:0 4px 14px rgba(99,102,241,0.35);padding:16px 32px;font-size:16px;">
        <span class="material-symbols-outlined" style="font-size:20px!important;">badge</span>
        Accéder à mon espace Assureur
      </button>
      <button class="landing-btn accent landing-cta-assure" style="padding:16px 32px;font-size:16px;">
        <span class="material-symbols-outlined" style="font-size:20px!important;">person</span>
        Accéder à mon espace Assuré
      </button>
    </div>
  </section>

  <!-- Portals Section -->
  <section class="landing-portals-section" id="portails">
    <div class="landing-section-title">
      <h2>Deux portails, une plateforme</h2>
      <p>Des interfaces adaptées à chaque acteur de l'assurance</p>
    </div>
    <div class="landing-portals-grid">
      <div class="landing-portal-card" style="border-color:rgba(99,102,241,0.2);">
        <div>
          <div class="landing-portal-header">
            <div class="landing-portal-icon" style="background:rgba(99,102,241,0.1);color:#6366f1;">
              <span class="material-symbols-outlined" style="font-size:28px!important;">badge</span>
            </div>
            <div>
              <div class="landing-portal-title">Assureur</div>
              <div class="landing-portal-subtitle">Courtier · Agent général · Compagnie</div>
            </div>
          </div>
          <p class="landing-portal-desc">
            Gérez votre portefeuille clients, réalisez des évaluations de risques
            multi-périls, et générez des avenants personnalisés — le tout depuis
            un tableau de bord centralisé.
          </p>
          <ul class="landing-portal-features">
            <li><span class="material-symbols-outlined">check_circle</span>Dashboard avec KPIs et tendances</li>
            <li><span class="material-symbols-outlined">check_circle</span>Risk Hub : localisation, actuariat, inspection 3D, évaluation</li>
            <li><span class="material-symbols-outlined">check_circle</span>Gestion de portefeuille et suivi clients</li>
            <li><span class="material-symbols-outlined">check_circle</span>Cartographie interactive des risques</li>
          </ul>
        </div>
        <button class="landing-btn primary landing-cta-assureur" style="background:#6366f1;box-shadow:0 4px 14px rgba(99,102,241,0.35);width:100%;justify-content:center;">
          <span class="material-symbols-outlined" style="font-size:18px!important;">login</span>
          Accéder à l'espace Assureur
        </button>
      </div>

      <div class="landing-portal-card" style="border-color:rgba(16,185,129,0.2);">
        <div>
          <div class="landing-portal-header">
            <div class="landing-portal-icon assure">
              <span class="material-symbols-outlined" style="font-size:28px!important;">person</span>
            </div>
            <div>
              <div class="landing-portal-title">Assuré</div>
              <div class="landing-portal-subtitle">Particulier · Professionnel</div>
            </div>
          </div>
          <p class="landing-portal-desc">
            Déclarez votre bien, visualisez son profil de risque climatique,
            découvrez les travaux recommandés pour améliorer votre score,
            et suivez l'évolution de vos garanties.
          </p>
          <ul class="landing-portal-features">
            <li><span class="material-symbols-outlined">check_circle</span>Formulaire assisté de votre bien</li>
            <li><span class="material-symbols-outlined">check_circle</span>Dashboard avec scores risques (inondation, argile, sismique)</li>
            <li><span class="material-symbols-outlined">check_circle</span>Visite 3D interactive de votre habitation</li>
            <li><span class="material-symbols-outlined">check_circle</span>Simulation de travaux et impact sur la prime</li>
          </ul>
        </div>
        <button class="landing-btn accent landing-cta-assure" style="width:100%;justify-content:center;">
          <span class="material-symbols-outlined" style="font-size:18px!important;">login</span>
          Accéder à mon espace Assuré
        </button>
      </div>
    </div>
  </section>

  <!-- Features Bento Section -->
  <section class="landing-bento-section" id="fonctionnalites">
    <div class="landing-section-title">
      <h2>Fonctionnalités clés</h2>
      <p>Une plateforme complète pour l'évaluation des risques climatiques</p>
    </div>
    <div class="landing-bento-grid">
      <div class="landing-bento-card col-span-2" style="background:linear-gradient(135deg,rgba(99,102,241,0.04),rgba(16,185,129,0.04));">
        <div class="landing-bento-icon" style="color:#6366f1;">
          <span class="material-symbols-outlined">map</span>
        </div>
        <h3>Cartographie multi-couches</h3>
        <p>Visualisez les zones inondables, l'aléa retrait-gonflement des argiles, la sismicité, et les risques industriels — directement depuis l'interface cartographique intégrée.</p>
      </div>
      <div class="landing-bento-card">
        <div class="landing-bento-icon" style="color:#10b981;">
          <span class="material-symbols-outlined">home</span>
        </div>
        <h3>Visualisation 3D</h3>
        <p>Inspectez votre bien en 3D, visualisez les composants à risque, et simulez l'impact des travaux de rénovation.</p>
      </div>
      <div class="landing-bento-card">
        <div class="landing-bento-icon" style="color:#f59e0b;">
          <span class="material-symbols-outlined">analytics</span>
        </div>
        <h3>Scoring actuariel</h3>
        <p>Évaluez le risque sur 5 périls (inondation, RGA, tempête, incendie, séisme) avec un scoring pondéré transparent.</p>
      </div>
      <div class="landing-bento-card">
        <div class="landing-bento-icon" style="color:#ef4444;">
          <span class="material-symbols-outlined">description</span>
        </div>
        <h3>Génération d'avenants</h3>
        <p>Générez automatiquement des avenants personnalisés avec calcul de la nouvelle prime et de la franchise.</p>
      </div>
      <div class="landing-bento-card">
        <div class="landing-bento-icon" style="color:#8b5cf6;">
          <span class="material-symbols-outlined">group</span>
        </div>
        <h3>Gestion de portefeuille</h3>
        <p>Suivez vos clients, leurs biens, leurs contrats, et l'historique des évaluations — le tout dans une interface unifiée.</p>
      </div>
      <div class="landing-bento-card">
        <div class="landing-bento-icon" style="color:#ec4899;">
          <span class="material-symbols-outlined">trending_up</span>
        </div>
        <h3>Projection 2050</h3>
        <p>Anticipez l'évolution des risques climatiques avec des projections à horizon 2050 basées sur les scénarios du GIEC.</p>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="landing-footer">
    <div class="landing-footer-content">
      <div style="display:flex;align-items:center;gap:8px;">
        <div class="landing-brand-icon" style="width:32px;height:32px;">
          <span class="material-symbols-outlined" style="font-size:18px!important;">auto_awesome</span>
        </div>
        <span style="font-size:16px;font-weight:600;color:var(--text-primary);">Prévia</span>
      </div>
      <p style="font-size:12px;">
        Plateforme d'évaluation des risques climatiques — Version Démo
      </p>
    </div>
  </footer>
</section>
"""

# Insert right after <body>
insert_marker = '<div class="dashboard-container">'
if landing_html.split('\n')[1].strip() not in content:
    content = content.replace(insert_marker, landing_html + '\n    ' + insert_marker)
    with open(os.path.join(project_root, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ Landing page added to index.html')
else:
    print('Landing page already exists')
