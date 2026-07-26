"""
Replace the sparse view-overview placeholder with a rich dashboard
modeled after the view-assure-bien style but adapted for the assureur.
"""
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The current view-overview HTML to replace
old_overview = '''        <section class="view-panel active" id="view-overview">
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
        </section>'''

# New rich overview modeled after view-assure-bien
new_overview = '''        <section class="view-panel active" id="view-overview">
          <!-- Overview-Style Cover Banner Section -->
          <section class="banner-section">
            <div class="banner-card">
              <!-- Fading carousel of French architecture background -->
              <div class="banner-gallery">
                <img class="banner-gallery-slide" src="https://images.unsplash.com/photo-1550340499-a6c60fc8287c?w=1200&q=50" alt="" loading="lazy" />
                <img class="banner-gallery-slide" src="https://images.unsplash.com/photo-1598965402089-897ce52e8355?w=1200&q=50" alt="" loading="lazy" />
                <img class="banner-gallery-slide" src="https://images.unsplash.com/photo-1589394815801-7cedad5d2cdc?w=1200&q=50" alt="" loading="lazy" />
                <img class="banner-gallery-slide" src="https://images.unsplash.com/photo-1485081669829-bacb8c7bb1f3?w=1200&q=50" alt="" loading="lazy" />
              </div>

              <!-- Left Info -->
              <div class="banner-info">
                <h1>Tableau de Bord<br>Portefeuille Risques</h1>
                <p id="overviewBannerAddress">Portefeuille de 6 clients · 8 biens immobiliers</p>
                <div class="team-avatars">
                  <span class="team-avatar-svg" style="background:#c56a3d;">JD</span>
                  <span class="team-avatar-svg" style="background:#10b981;">MB</span>
                  <span class="team-avatar-svg" style="background:#3b82f6;">PL</span>
                  <span class="team-avatar-svg" style="background:#8b5cf6;" id="overviewPolicyTag">MRH</span>
                </div>
              </div>

              <!-- Floating Glassmorphism Quick Action Card -->
              <div class="floating-task-card">
                <div class="floating-task-header">
                  <div>
                    <h3 id="overviewQuickTitle">Soumissions en attente</h3>
                    <span class="task-date" id="overviewQuickDesc">3 dossiers à examiner</span>
                  </div>
                  <span class="material-symbols-outlined arrow-icon">arrow_forward</span>
                </div>
                <div class="floating-task-progress">
                  <span class="progress-val" id="overviewQuickVal">3</span>
                  <span class="progress-indicator-dot"></span>
                </div>
              </div>

              <!-- Right Completion Card (Glassmorphic Stats & Chart) -->
              <div class="banner-completion-card">
                <div class="completion-header">
                  <div>
                    <span class="completion-label">Score de risque moyen</span>
                    <h2 id="overviewBannerScore">62</h2>
                  </div>
                  <span class="trend-indicator positive" id="overviewBannerTrend">-8 pts ▲</span>
                </div>

                <!-- Sparkline Line Chart -->
                <div class="sparkline-chart">
                  <svg viewBox="0 0 200 80" preserveAspectRatio="none">
                    <defs>
                      <linearGradient id="chart-grad-overview" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stop-color="rgba(255, 255, 255, 0.4)" />
                        <stop offset="100%" stop-color="rgba(255, 255, 255, 0.0)" />
                      </linearGradient>
                    </defs>
                    <path d="M 0,65 Q 30,55 60,40 T 120,50 T 160,25 T 200,35" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round"/>
                    <path d="M 0,65 Q 30,55 60,40 T 120,50 T 160,25 T 200,35 L 200,80 L 0,80 Z" fill="url(#chart-grad-overview)"/>
                    <circle cx="160" cy="25" r="4" fill="#ffffff" stroke="rgba(255, 255, 255, 0.5)" stroke-width="3"/>
                  </svg>
                </div>

                <div class="completion-footer">
                  <div class="footer-stat">
                    <span class="footer-stat-label" id="overviewStatClients">6 clients</span>
                  </div>
                  <div class="segmented-progress">
                    <span class="seg active"></span>
                    <span class="seg active"></span>
                    <span class="seg active"></span>
                    <span class="seg active"></span>
                    <span class="seg"></span>
                  </div>
                  <div class="footer-stat align-right">
                    <span class="footer-stat-label" id="overviewStatSecurises">4 sécurisés</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- Dashboard Widgets Grid -->
          <section class="widgets-grid">
            <div class="grid-column col-span-2">
              <!-- Portfolio Stats Cards Row -->
              <div class="dashboard-stats-row" style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:12px;">
                <div class="dashboard-card" style="padding:14px;">
                  <span class="material-symbols-outlined" style="font-size:18px;color:var(--color-primary);">group</span>
                  <span class="stat-card-value" style="font-size:22px;font-weight:600;display:block;" id="ovStatTotalClients">6</span>
                  <span class="stat-card-label" style="font-size:10px;color:var(--text-muted);">Clients</span>
                </div>
                <div class="dashboard-card" style="padding:14px;">
                  <span class="material-symbols-outlined" style="font-size:18px;color:var(--color-primary);">home</span>
                  <span class="stat-card-value" style="font-size:22px;font-weight:600;display:block;" id="ovStatTotalProps">8</span>
                  <span class="stat-card-label" style="font-size:10px;color:var(--text-muted);">Biens</span>
                </div>
                <div class="dashboard-card" style="padding:14px;">
                  <span class="material-symbols-outlined" style="font-size:18px;color:var(--color-primary);">assessment</span>
                  <span class="stat-card-value" style="font-size:22px;font-weight:600;display:block;" id="ovStatAssessments">5</span>
                  <span class="stat-card-label" style="font-size:10px;color:var(--text-muted);">Evaluations</span>
                </div>
              </div>

              <!-- Vulnerability Distribution Card -->
              <div class="dashboard-card cross-section-card">
                <div class="card-header">
                  <h3>Répartition des risques</h3>
                  <span class="material-symbols-outlined action-icon">north_east</span>
                </div>
                <div class="card-body">
                  <div class="card-metric">
                    <h2 id="overviewPropScore">62% <span class="trend positive" id="overviewPropRisk">Risque Modéré</span></h2>
                    <span class="legend-indicator">Moyenne pondérée du portefeuille</span>
                  </div>
                  <div class="bar-chart-container">
                    <div class="chart-bars">
                      <div class="bar" style="height: 30%"></div>
                      <div class="bar" style="height: 35%"></div>
                      <div class="bar" style="height: 40%"></div>
                      <div class="bar" style="height: 45%"></div>
                      <div class="bar" style="height: 50%"></div>
                      <div class="bar highlight" style="height: 60%"></div>
                      <div class="bar highlight" style="height: 70%"></div>
                      <div class="bar highlight" style="height: 80%"></div>
                      <div class="bar highlight" style="height: 70%"></div>
                      <div class="bar highlight" style="height: 60%"></div>
                      <div class="bar" style="height: 50%"></div>
                      <div class="bar" style="height: 45%"></div>
                      <div class="bar" style="height: 40%"></div>
                      <div class="bar" style="height: 35%"></div>
                      <div class="bar" style="height: 30%"></div>
                    </div>
                    <div class="chart-labels">
                      <span>0</span><span>20</span><span>40</span><span>60</span><span>80</span><span>100</span>
                    </div>
                  </div>
                  <div class="assure-prop-grid" style="margin-top:16px;padding-top:14px;border-top:1px solid var(--border-color);">
                    <div class="assure-prop-item">
                      <span class="assure-prop-label">Portefeuille</span>
                      <span class="assure-prop-value" id="overviewPropPortfolio">8 biens · 6 clients</span>
                    </div>
                    <div class="assure-prop-item">
                      <span class="assure-prop-label">Villes couvertes</span>
                      <span class="assure-prop-value" id="overviewPropCities">Paris, Bordeaux, Toulouse, Lille</span>
                    </div>
                    <div class="assure-prop-item">
                      <span class="assure-prop-label">Score moyen</span>
                      <span class="assure-prop-value" id="overviewPropAvgScore">62 / 100</span>
                    </div>
                    <div class="assure-prop-item">
                      <span class="assure-prop-label">Haut risque</span>
                      <span class="assure-prop-value" id="overviewPropHighRisk">2 biens</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Savings / Performance Card -->
              <div class="dashboard-card distance-card">
                <div class="distance-metric">
                  <h2 id="overviewStatSavings">15 200 € <span class="trend positive">-12% ▼</span></h2>
                  <div class="distance-progress-group">
                    <span class="date-label">Prime totale estimée du portefeuille</span>
                    <md-linear-progress value="0.60" class="progress-bar-custom"></md-linear-progress>
                  </div>
                  <span class="legend-indicator" id="overviewStatEngagement">4 clients actifs</span>
                </div>
              </div>
            </div>

            <div class="grid-column col-span-3">
              <!-- Circular Progresses Row -->
              <div class="circular-cards-row">
                <!-- Flood -->
                <div class="dashboard-card circ-widget">
                  <div class="widget-header">
                    <h3>Risque inondation</h3>
                    <span class="material-symbols-outlined action-icon">north_east</span>
                  </div>
                  <div class="circ-body">
                    <div class="circ-kpi">
                      <span class="circ-pct" id="ovGaugeFloodVal">72%</span>
                      <span class="circ-trend negative">Elevé</span>
                    </div>
                    <div class="circ-ring">
                      <svg viewBox="0 0 100 100">
                        <path d="M 5 50 A 45 45 0 0 1 50 5" fill="none" stroke="var(--border-color)" stroke-width="10" stroke-linecap="round"/>
                        <path id="ovGaugeFlood" d="M 5 50 A 45 45 0 0 1 50 5" fill="none" stroke="#ef4444" stroke-width="10" stroke-linecap="round" stroke-dasharray="70.685" stroke-dashoffset="19.79"/>
                      </svg>
                    </div>
                  </div>
                </div>

                <!-- Clay -->
                <div class="dashboard-card circ-widget">
                  <div class="widget-header">
                    <h3>Retrait argile</h3>
                    <span class="material-symbols-outlined action-icon">north_east</span>
                  </div>
                  <div class="circ-body">
                    <div class="circ-kpi">
                      <span class="circ-pct" id="ovGaugeClayVal">58%</span>
                      <span class="circ-trend positive">Modéré</span>
                    </div>
                    <div class="circ-ring">
                      <svg viewBox="0 0 100 100">
                        <path d="M 5 50 A 45 45 0 0 1 50 5" fill="none" stroke="var(--border-color)" stroke-width="10" stroke-linecap="round"/>
                        <path id="ovGaugeClay" d="M 5 50 A 45 45 0 0 1 50 5" fill="none" stroke="#f59e0b" stroke-width="10" stroke-linecap="round" stroke-dasharray="70.685" stroke-dashoffset="25.45"/>
                      </svg>
                    </div>
                  </div>
                </div>

                <!-- Seismic -->
                <div class="dashboard-card circ-widget">
                  <div class="widget-header">
                    <h3>Risque sismique</h3>
                    <span class="material-symbols-outlined action-icon">north_east</span>
                  </div>
                  <div class="circ-body">
                    <div class="circ-kpi">
                      <span class="circ-pct" id="ovGaugeSeismicVal">36%</span>
                      <span class="circ-trend positive">Faible</span>
                    </div>
                    <div class="circ-ring">
                      <svg viewBox="0 0 100 100">
                        <path d="M 5 50 A 45 45 0 0 1 50 5" fill="none" stroke="var(--border-color)" stroke-width="10" stroke-linecap="round"/>
                        <path id="ovGaugeSeismic" d="M 5 50 A 45 45 0 0 1 50 5" fill="none" stroke="#3b82f6" stroke-width="10" stroke-linecap="round" stroke-dasharray="70.685" stroke-dashoffset="40"/>
                      </svg>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Activity / Recent Submissions Card -->
              <div class="dashboard-card">
                <div class="card-header">
                  <h3>Soumissions récentes</h3>
                  <span class="material-symbols-outlined action-icon">north_east</span>
                </div>
                <div class="card-body">
                  <div style="display:flex;flex-direction:column;gap:10px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:var(--bg-panel);border-radius:var(--border-radius-sm);">
                      <div style="display:flex;align-items:center;gap:10px;">
                        <span class="material-symbols-outlined" style="color:#ef4444;">home</span>
                        <div>
                          <div style="font-size:13px;font-weight:600;color:var(--text-primary);">Jean Dupont · 8 Rue de la Paix</div>
                          <div style="font-size:11px;color:var(--text-muted);">Soumis le 24/07/2026 · Score 72%</div>
                        </div>
                      </div>
                      <span style="font-size:11px;padding:3px 8px;border-radius:12px;background:rgba(245,158,11,0.15);color:#f59e0b;font-weight:500;">En attente</span>
                    </div>

                    <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:var(--bg-panel);border-radius:var(--border-radius-sm);">
                      <div style="display:flex;align-items:center;gap:10px;">
                        <span class="material-symbols-outlined" style="color:#10b981;">home</span>
                        <div>
                          <div style="font-size:13px;font-weight:600;color:var(--text-primary);">Marie Bernard · 15 Bd Haussmann</div>
                          <div style="font-size:11px;color:var(--text-muted);">Soumis le 22/07/2026 · Score 45%</div>
                        </div>
                      </div>
                      <span style="font-size:11px;padding:3px 8px;border-radius:12px;background:rgba(16,185,129,0.15);color:#10b981;font-weight:500;">Complété</span>
                    </div>

                    <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:var(--bg-panel);border-radius:var(--border-radius-sm);">
                      <div style="display:flex;align-items:center;gap:10px;">
                        <span class="material-symbols-outlined" style="color:#3b82f6;">home</span>
                        <div>
                          <div style="font-size:13px;font-weight:600;color:var(--text-primary);">Pierre Lefèvre · 34 Rue de Rivoli</div>
                          <div style="font-size:11px;color:var(--text-muted);">Soumis le 20/07/2026 · Score 88%</div>
                        </div>
                      </div>
                      <span style="font-size:11px;padding:3px 8px;border-radius:12px;background:rgba(239,68,68,0.15);color:#ef4444;font-weight:500;">Haut risque</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </section>'''

if old_overview in content:
    content = content.replace(old_overview, new_overview, 1)
    print("✅ view-overview replaced with rich dashboard")
else:
    print("⚠️ Could not find old overview - trying partial match...")
    # Try to find by id pattern
    import re
    pattern = r'<section class="view-panel active" id="view-overview">.*?</section>\s*(?=<!-- PORTFOLIO -->|<section class="view-panel")'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content.replace(match.group(0), new_overview)
        print("✅ view-overview replaced via regex")
    else:
        print("❌ Could not find view-overview at all")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ index.html written ({len(content)} chars)")
