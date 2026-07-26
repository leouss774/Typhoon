/**
 * Portfolio view module.
 * Loads data from API via data-service.ts and renders the property grid dynamically.
 * Sub-tabs: Summary, Map, Trends
 */
import { fetchClientsFromApi, fetchPropertiesFromApi, isApiAvailable } from '../../api/data-service.js';
import { initPortfolioMap, destroyPortfolioMap } from './portfolio-map.js';

let initialized = false;

export function initPortfolio(): void {
  if (initialized) return;
  initialized = true;
  loadPortfolioData();

  // Initialize map if the Map sub-tab is active
  const mapTab = document.querySelector('.portfolio-tab-content[data-content="map"]');
  if (mapTab?.classList.contains('active')) {
    requestAnimationFrame(() => initPortfolioMap());
  }
}

export function destroyPortfolio(): void {
  initialized = false;
  destroyPortfolioMap();
}

export function onPortfolioTabChange(tabKey: string): void {
  if (tabKey === 'map') {
    requestAnimationFrame(() => initPortfolioMap());
  } else {
    destroyPortfolioMap();
  }
}

/* ── Load data from API ───────────────────────────── */

async function loadPortfolioData(): Promise<void> {
  const properties = await fetchPropertiesFromApi();
  const clients = await fetchClientsFromApi();

  if (!isApiAvailable() || properties.length === 0) {
    showApiFallback();
    return;
  }

  renderKpis(properties, clients);
  renderPropertyGrid(properties, clients);
  renderDistCard(properties);
}

/* ── API fallback message ─────────────────────────── */

function showApiFallback(): void {
  const grid = document.getElementById('portfolioGrid');
  if (grid) {
    grid.innerHTML = `<div style="grid-column:1/-1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:60px 20px;gap:12px;background:var(--bg-card);border-radius:var(--border-radius-md);">
      <span class="material-symbols-outlined" style="font-size:48px;color:var(--text-muted);opacity:0.3;">cloud_off</span>
      <p style="font-size:14px;color:var(--text-secondary);text-align:center;">API du backend non disponible.<br>Vérifiez que le serveur backend est lancé avec <code style="font-size:12px;background:var(--bg-panel);padding:2px 6px;border-radius:4px;">cd backend && npm run dev</code></p>
    </div>`;
  }

  // Set KPI values to dashes
  ['portKpiProperties', 'portKpiHighRisk', 'portKpiAvgScore', 'portKpiImpact', 'portKpiCities'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = '—';
  });
}

/* ── Render KPIs ──────────────────────────────────── */

function renderKpis(properties: any[], clients: any[]): void {
  const highRisk = properties.filter(p => (p.riskLevel === 'high' || p.riskScore > 60)).length;
  const avgScore = properties.length > 0
    ? Math.round(properties.reduce((s, p) => s + (p.riskScore || 0), 0) / properties.length)
    : 0;

  // Collect unique cities from properties
  const cities = new Set<string>();
  properties.forEach(p => {
    if (p.city) cities.add(p.city);
    // Also try address parsing for city
    const addr = p.address || '';
    const parts = addr.split(',');
    if (parts.length > 1) {
      const last = parts[parts.length - 1].trim();
      const cityMatch = last.match(/\d{5}\s+(.+)/);
      if (cityMatch) cities.add(cityMatch[1]);
    }
  });

  setText('portKpiProperties', String(properties.length));
  setText('portKpiHighRisk', String(highRisk));
  setText('portKpiAvgScore', String(avgScore));
  setText('portKpiImpact', '−' + avgScore * 1.8 + 'K€');
  setText('portKpiCities', String(cities.size || '—'));
}

/* ── Render property grid ─────────────────────────── */

function renderPropertyGrid(properties: any[], clients: any[]): void {
  const grid = document.getElementById('portfolioGrid');
  if (!grid) return;

  // Build a client lookup map
  const clientMap = new Map<string, any>();
  clients.forEach(c => clientMap.set(c.id, c));

  grid.innerHTML = properties.map(p => {
    const client = clientMap.get(p.clientId);
    const initials = client
      ? (client.firstName?.[0] || '') + (client.lastName?.[0] || '')
      : '?';
    const clientName = client
      ? `${client.firstName || ''} ${client.lastName || ''}`.trim()
      : 'Client inconnu';
    const score = p.riskScore || 0;
    const level = score > 60 ? 'high' : score > 35 ? 'medium' : 'low';
    const addr = p.address?.split(',')[0] || 'Adresse inconnue';
    const dpe = p.dpeClass ? ` · DPE: ${p.dpeClass}` : '';
    const shortAddr = addr.length > 30 ? addr.substring(0, 28) + '…' : addr;

    return `<div class="portfolio-prop ${level}" data-addr="${p.address || ''}" data-client="${clientName}">
      <div class="portfolio-prop-top">
        <span class="risk-dot ${level}"></span>
        <span class="portfolio-prop-addr">${shortAddr}</span>
        <span class="portfolio-prop-client">${initials}</span>
      </div>
      <div class="portfolio-prop-mid">
        <span class="portfolio-prop-score">${score}</span>
        <span class="portfolio-prop-label">Score de risque</span>
      </div>
      <div class="portfolio-prop-btm">${p.city || ''}${dpe}</div>
    </div>`;
  }).join('');
}

/* ── Render distribution card (static with real counts) ── */

function renderDistCard(properties: any[]): void {
  const highCount = properties.filter(p => (p.riskLevel === 'high' || p.riskScore > 60)).length;
  const medCount = properties.filter(p => p.riskScore > 35 && p.riskScore <= 60).length;
  const lowCount = properties.filter(p => p.riskScore <= 35 || p.riskLevel === 'low').length;
  const total = properties.length || 1;

  // Update the SVG ring and legend if they exist
  const distPct = document.querySelector('.portfolio-dist-pct');
  if (distPct) distPct.textContent = String(total);

  const countEls = document.querySelectorAll('.portfolio-dist-count');
  if (countEls.length >= 3) {
    (countEls[0] as HTMLElement).textContent = String(highCount);
    (countEls[1] as HTMLElement).textContent = String(medCount);
    (countEls[2] as HTMLElement).textContent = String(lowCount);
  }

  // Update SVG ring proportions (approximate)
  const circles = document.querySelectorAll('.portfolio-dist-ring svg circle');
  if (circles.length >= 4) {
    const highPct = (highCount / total) * 100;
    const medPct = (medCount / total) * 100;
    // Adjust dash offsets to reflect proportions
    (circles[1] as SVGElement).setAttribute('stroke-dasharray', String(highPct));
    (circles[2] as SVGElement).setAttribute('stroke-dasharray', String(medPct));
    (circles[3] as SVGElement).setAttribute('stroke-dasharray', String(lowCount / total * 100));
  }
}

/* ── Helpers ──────────────────────────────────────── */

function setText(id: string, text: string): void {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}
