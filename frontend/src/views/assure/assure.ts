/**
 * Espace Assuré — Client Portal view module.
 *
 * Provides view lifecycle and state management for the Assuré pages:
 *   assure-bien        → Mon Bien (property card + climate risk gauges)
 *   assure-travaux     → Mes Travaux (3D house + component selection)
 *   assure-engagement  → Mon Engagement (score gauges + premium impact + sign CTA)
 *   assure-dossier     → Mon Dossier (assessment history + documents + advisor contact)
 */

import { store } from '../../data.js';
import { housePartData, initHouse, destroyHouse } from '../../house3d.js';
import { navContext } from '../../context.js';
import { navigateTo } from '../../router.js';

/* ═══════════════════════════════════════════════════════════════
   Types
   ═══════════════════════════════════════════════════════════════ */

interface AssureState {
  selectedClientId: string | null;
  selectedPropertyId: string | null;
  selectedWorks: Set<string>;
  engagementSigned: boolean;
}

/* ═══════════════════════════════════════════════════════════════
   State
   ═══════════════════════════════════════════════════════════════ */

let initialized = false;
const state: AssureState = {
  selectedClientId: null,
  selectedPropertyId: null,
  selectedWorks: new Set(),
  engagementSigned: false,
};

/* ═══════════════════════════════════════════════════════════════
   Exported API (router lifecycle contract)
   ═══════════════════════════════════════════════════════════════ */

export function initAssure(viewName: string = 'assure-bien'): void {
  if (!initialized) {
    initialized = true;
    loadClientData();
    setupSignModal();
    setupCrossTabNavigation();
    setupPropertyForm();
    initCustomDropdowns();
    initUploadZone();
    setupModeToggle();
  }

  // Render content based on current view
  renderBien();
  renderTravaux();
  renderEngagement();
  renderDossier();

  // Check if property form is completed → show dashboard by default
  if (viewName === 'assure-bien') {
    const formCompleted = localStorage.getItem('assure_form_completed') === '1';
    const formView = document.getElementById('assureFormView');
    const dashView = document.getElementById('assureDashView');
    const modeSelector = document.getElementById('assureModeSelector');
    if (formCompleted && formView && dashView && modeSelector) {
      formView.style.display = 'none';
      dashView.style.display = '';
      modeSelector.style.display = 'flex';
      document.querySelectorAll('.assure-mode-btn').forEach(b => b.classList.remove('active'));
      document.getElementById('assureModeDashBtn')?.classList.add('active');
      // Pre-fill dashboard with stored data
      loadPropertyDataIntoDashboard();
    } else if (formView && modeSelector) {
      formView.style.display = '';
      modeSelector.style.display = 'none'; // Hide toggle until form is completed
    }
  }

  if (viewName === 'assure-travaux') {
    requestAnimationFrame(() => {
      initHouse('assureHouseContainer');
    });
  }

  console.log(`[Assure] View ${viewName} initialized`);
}

export function destroyAssure(): void {
  destroyHouse();
  initialized = false;
}

/* ═══════════════════════════════════════════════════════════════
   Data loading
   ═══════════════════════════════════════════════════════════════ */

function loadClientData(): void {
  const ctx = navContext.context;
  if (ctx.selectedClientId) state.selectedClientId = ctx.selectedClientId;
  if (ctx.selectedPropertyId) state.selectedPropertyId = ctx.selectedPropertyId;

  if (!state.selectedClientId) {
    const clients = store.getAllClients();
    if (clients.length > 0) {
      state.selectedClientId = clients[0].id;
      const props = store.getClientProperties(state.selectedClientId);
      if (props.length > 0) state.selectedPropertyId = props[0].id;
    }
  }

  if (state.selectedWorks.size === 0) {
    state.selectedWorks = new Set(Object.keys(housePartData));
  }
}

/* ═══════════════════════════════════════════════════════════════
   Helpers
   ═══════════════════════════════════════════════════════════════ */

function setText(id: string, text: string): void {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function getColorForScore(score: number): string {
  if (score >= 70) return '#ef4444';
  if (score >= 50) return '#f59e0b';
  if (score >= 30) return '#3b82f6';
  return '#10b981';
}

function getRiskLabel(score: number): string {
  if (score >= 70) return 'Risque Élevé';
  if (score >= 50) return 'Risque Modéré';
  if (score >= 30) return 'Risque Faible';
  return 'Risque Minime';
}

function computeCurrentScore(): number {
  const comps = Object.values(housePartData);
  if (comps.length === 0) return 0;
  return Math.round(comps.reduce((s, c) => s + c.score, 0) / comps.length);
}

function computeProjectedScore(selectedIds: string[]): number {
  const comps = Object.values(housePartData);
  if (comps.length === 0) return 0;
  const total = comps.reduce((s, c) =>
    s + (selectedIds.includes(c.id) ? Math.max(0, c.score - Math.round(c.score * 0.55)) : c.score), 0);
  return Math.round(total / comps.length);
}

function computeAnnualSavings(selectedIds: string[]): number {
  let total = 0;
  for (const c of Object.values(housePartData)) {
    if (selectedIds.includes(c.id)) {
      const match = c.annualSavings.replace(/\s/g, '').match(/([0-9]+)/);
      if (match) total += parseInt(match[1], 10);
    }
  }
  return total;
}

function computeTotalCost(selectedIds: string[]): number {
  let total = 0;
  for (const c of Object.values(housePartData)) {
    if (selectedIds.includes(c.id)) {
      const match = c.cost.replace(/\s/g, '').match(/([0-9]+)/);
      if (match) total += parseInt(match[1], 10);
    }
  }
  return total;
}

function updateGauge(arcId: string, valId: string, score: number, color: string): void {
  const circumference = 314; // 2 * π * 50
  const offset = circumference - (score / 100) * circumference;
  const arc = document.getElementById(arcId) as SVGElement | null;
  const val = document.getElementById(valId);
  if (arc) {
    arc.setAttribute('stroke-dashoffset', String(offset));
    arc.setAttribute('stroke', color);
  }
  if (val) val.textContent = String(score);
}

/* ═══════════════════════════════════════════════════════════════
   Cross-page navigation
   ═══════════════════════════════════════════════════════════════ */

function setupCrossTabNavigation(): void {
  const nextBtn = document.getElementById('assureTravauxNextBtn');
  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      navigateTo('assure-engagement');
    });
  }
}

/* ═══════════════════════════════════════════════════════════════
   MON BIEN — Property overview + risk gauges
   ═══════════════════════════════════════════════════════════════ */

function renderBien(): void {
  const client = state.selectedClientId ? store.getClient(state.selectedClientId) : null;
  const prop = state.selectedPropertyId ? store.getProperty(state.selectedPropertyId) : null;
  const currentScore = computeCurrentScore();
  const works = Array.from(state.selectedWorks);
  const projectedScore = computeProjectedScore(works);
  const savings = computeAnnualSavings(works);

  if (client) {
    setText('assureBannerName', `${client.civility} ${client.firstName} ${client.lastName}`);
    setText('assureBannerPolicy', client.policyNumber);
  }
  if (prop) {
    setText('assureBannerAddress', `${prop.address}, ${prop.city}`);
  }
  setText('assureBannerScore', `${currentScore}%`);
  setText('assureBannerRisk', getRiskLabel(currentScore));

  setText('assureStatScore', String(currentScore));
  setText('assureStatSavings', `${savings.toLocaleString('fr-FR')} €/an`);
  const engEl = document.getElementById('assureStatEngagement');
  if (engEl) {
    engEl.textContent = state.engagementSigned ? 'Engagement signé' : 'En attente de signature';
    engEl.style.color = state.engagementSigned ? '#10b981' : 'var(--text-muted)';
  }

  if (prop) {
    setText('assurePropAddress', prop.address);
    setText('assurePropCity', prop.city);
    setText('assurePropDpe', prop.dpeClass);
    setText('assurePropYear', String(prop.builtYear));
    setText('assurePropRisk', getRiskLabel(prop.riskScore));
    setText('assurePropScore', `${prop.riskScore}%`);
  }

  // Real Géorisques scores from Property entity (or fallback)
  let floodScore = Math.min(100, Math.round(currentScore * 1.15));
  let clayScore = Math.min(100, Math.round(currentScore * 0.9));
  let seismicScore = Math.min(100, Math.round(currentScore * 0.55));

  if (prop?.georisques) {
    const g = prop.georisques;
    const floodMap = { rouge: 85, bleu: 60, blanc: 30, non_concerne: 10 };
    const clayMap = { 'très fort': 90, fort: 70, moyen: 45, faible: 15 };
    const seismicMap = { 5: 90, 4: 70, 3: 50, 2: 30, 1: 10 };

    floodScore = floodMap[g.floodZone] ?? floodScore;
    clayScore = clayMap[g.clayRiskIndex] ?? clayScore;
    seismicScore = seismicMap[g.seismicZone] ?? seismicScore;
  }

  const gaugeData = [
    { arcId: 'assurGaugeBienFlood', valId: 'assurGaugeBienFloodVal', score: floodScore },
    { arcId: 'assurGaugeBienClay', valId: 'assurGaugeBienClayVal', score: clayScore },
    { arcId: 'assurGaugeBienSeismic', valId: 'assurGaugeBienSeismicVal', score: seismicScore },
  ];

  for (const g of gaugeData) {
    const color = getColorForScore(g.score);
    const totalArcLen = 70.685;
    const offset = totalArcLen - (g.score / 100) * totalArcLen;
    const arc = document.getElementById(g.arcId) as SVGElement | null;
    const val = document.getElementById(g.valId);
    if (arc) {
      arc.setAttribute('stroke-dashoffset', String(offset.toFixed(2)));
      arc.setAttribute('stroke', color);
    }
    if (val) val.textContent = String(g.score) + '%';
  }

  const diff = currentScore - projectedScore;
  setText('assureBienImprove', diff > 0 ? `−${diff} pts ▲` : 'Score optimal');
}

/* ═══════════════════════════════════════════════════════════════
   MES TRAVAUX — 3D house + component selection
   ═══════════════════════════════════════════════════════════════ */

function renderTravaux(): void {
  renderComponentGrid();
  renderWorksSummary();
}

function renderComponentGrid(): void {
  const grid = document.getElementById('assureCompGrid');
  if (!grid) return;

  grid.innerHTML = Object.values(housePartData).map(c => {
    const selected = state.selectedWorks.has(c.id);
    return `
    <div class="assure-comp-card ${selected ? 'selected' : ''}" data-comp="${c.id}">
      <div class="assure-comp-card-header">
        <span class="assure-comp-card-name">
          <span class="material-symbols-outlined" style="font-size:14px!important;vertical-align:middle;margin-right:3px;">${getPartIcon(c.id)}</span>
          ${c.label}
        </span>
        <label class="assure-comp-toggle" title="Inclure dans les travaux">
          <input type="checkbox" class="assure-comp-check" data-comp="${c.id}" ${selected ? 'checked' : ''}>
          <span class="assure-comp-checkmark"></span>
        </label>
      </div>
      <span class="assure-comp-risk-badge ${c.risk}">${getRiskLabel(c.score)}</span>
      <p class="assure-comp-desc">${c.description}</p>
      <div class="assure-comp-footer">
        <span>Coût estimé : <strong>${c.cost}</strong></span>
        <span class="assure-comp-saving">Éco. ${c.annualSavings}</span>
      </div>
    </div>`;
  }).join('');

  grid.querySelectorAll('.assure-comp-check').forEach(cb => {
    cb.addEventListener('change', () => {
      const compId = (cb as HTMLInputElement).getAttribute('data-comp');
      if (!compId) return;
      if ((cb as HTMLInputElement).checked) {
        state.selectedWorks.add(compId);
      } else {
        state.selectedWorks.delete(compId);
      }
      renderComponentGrid();
      renderWorksSummary();
      renderEngagement();
    });
  });
}

function getPartIcon(id: string): string {
  const icons: Record<string, string> = {
    roof: 'roofing',
    walls: 'layers',
    basement: 'foundation',
    windows: 'window',
    plumbing: 'plumbing',
    heating: 'local_fire_department',
  };
  return icons[id] || 'home_repair_service';
}

function renderWorksSummary(): void {
  const works = Array.from(state.selectedWorks);
  const cost = computeTotalCost(works);
  const savings = computeAnnualSavings(works);
  const annualPremium = getAnnualPremium();
  const newPremium = Math.max(0, annualPremium - savings);

  setText('assureTravauxCost', `${cost.toLocaleString('fr-FR')} €`);
  setText('assureTravauxSavings', `${savings.toLocaleString('fr-FR')} €/an`);
  setText('assureTravauxPremium', `${newPremium.toLocaleString('fr-FR')} €/an`);

  const listEl = document.getElementById('assureWorksList');
  if (!listEl) return;

  const selectedComps = Object.values(housePartData).filter(c => works.includes(c.id));
  if (selectedComps.length === 0) {
    listEl.innerHTML = '<span class="assure-works-empty">Cochez des composants ci-dessus pour voir les travaux recommandés.</span>';
    return;
  }
  listEl.innerHTML = selectedComps.map(c => `
    <div class="assure-works-item">
      <span class="assure-works-item-name">${c.label}</span>
      <ul class="assure-works-item-list">
        ${c.works.map(w => `<li>${w}</li>`).join('')}
      </ul>
    </div>
  `).join('');
}

/* ═══════════════════════════════════════════════════════════════
   MON ENGAGEMENT — score gauges + premium impact + sign CTA
   ═══════════════════════════════════════════════════════════════ */

function renderEngagement(): void {
  const works = Array.from(state.selectedWorks);
  const currentScore = computeCurrentScore();
  const projectedScore = computeProjectedScore(works);
  const annualPremium = getAnnualPremium();
  const savings = computeAnnualSavings(works);
  const newPremium = Math.max(0, annualPremium - savings);
  const totalCost = computeTotalCost(works);
  const diff = currentScore - projectedScore;

  updateGauge('assureGaugeArcCurrent', 'assureGaugeValCurrent', currentScore, getColorForScore(currentScore));
  updateGauge('assureGaugeArcProjected', 'assureGaugeValProjected', projectedScore, getColorForScore(projectedScore));

  const improvEl = document.getElementById('assureImproveVal');
  if (improvEl) {
    improvEl.textContent = diff > 0 ? `−${diff} pts` : diff === 0 ? '0 pts' : `+${Math.abs(diff)} pts`;
    improvEl.style.color = diff > 0 ? '#10b981' : diff === 0 ? 'var(--text-muted)' : 'var(--color-danger)';
  }

  setText('assureEngPremiumCurrent', `${annualPremium.toLocaleString('fr-FR')} €/an`);
  setText('assureEngPremiumNew', `${newPremium.toLocaleString('fr-FR')} €/an`);
  setText('assureEngPremiumSaving', `− ${savings.toLocaleString('fr-FR')} €/an`);

  const reductionPct = annualPremium > 0 ? Math.round((savings / annualPremium) * 100) : 0;
  const paybackYears = savings > 0 ? Math.ceil(totalCost / savings) : 0;
  setText('assureRecapReduc', `-${reductionPct}%`);
  setText('assureRecapImprov', diff > 0 ? `-${diff} pts` : '0 pts');
  setText('assureRecapPayback', paybackYears > 0 ? `${paybackYears} ans` : '—');

  const worksEl = document.getElementById('assureAvenantWorks');
  if (worksEl) {
    const selected = Object.values(housePartData).filter(c => works.includes(c.id));
    if (selected.length === 0) {
      worksEl.innerHTML = '<p style="font-size:12px;color:var(--text-muted);">Aucun travail sélectionné — rendez-vous sur "Mes Travaux" pour en choisir.</p>';
    } else {
      worksEl.innerHTML = selected.map(c => `
        <div class="assure-avenant-works-item">
          <span class="material-symbols-outlined" style="color:#10b981;">check_circle</span>
          <span>${c.label}</span>
          <span style="margin-left:auto;font-size:11px;color:var(--text-muted);">${c.cost}</span>
        </div>
      `).join('');
    }
  }

  const client = state.selectedClientId ? store.getClient(state.selectedClientId) : null;
  const prop = state.selectedPropertyId ? store.getProperty(state.selectedPropertyId) : null;
  if (client) {
    setText('assurePolNumber', client.policyNumber);
    setText('assurePolClient', `${client.civility} ${client.firstName} ${client.lastName}`);
    setText('assurePolPremiumCurrent', `${annualPremium.toLocaleString('fr-FR')} €`);
  }
  if (prop) {
    setText('assurePolProperty', prop.address + ', ' + prop.city);
  }
  setText('assurePolPremiumNew', `${newPremium.toLocaleString('fr-FR')} €`);

  const signBtn = document.getElementById('assureSignBtn') as HTMLButtonElement | null;
  if (signBtn) {
    signBtn.disabled = works.length === 0;
  }
}

/* ═══════════════════════════════════════════════════════════════
   MON DOSSIER — assessment history + documents + advisor
   ═══════════════════════════════════════════════════════════════ */

function renderDossier(): void {
  const client = state.selectedClientId ? store.getClient(state.selectedClientId) : null;
  if (!client) return;

  const historyEl = document.getElementById('assureHistoryList');
  if (historyEl) {
    const assessments = store.getClientAssessments(client.id);
    if (assessments.length === 0) {
      historyEl.innerHTML = '<span class="assure-works-empty">Aucune évaluation disponible.</span>';
    } else {
      historyEl.innerHTML = assessments.map(a => `
        <div class="assure-history-item">
          <div class="assure-history-icon">
            <span class="material-symbols-outlined">analytics</span>
          </div>
          <div class="assure-history-info">
            <div class="assure-history-title">Évaluation · ${a.date}</div>
            <div class="assure-history-meta">${a.riskSummary} · ${a.pages} pages</div>
          </div>
          <span class="assure-history-score" style="color:${getColorForScore(a.score)};">${a.score}</span>
        </div>
      `).join('');
    }
  }

  const docsEl = document.getElementById('assureDocList');
  if (docsEl) {
    const docs = store.getClientDocuments(client.id);
    if (docs.length === 0) {
      docsEl.innerHTML = '<span class="assure-works-empty">Aucun document disponible.</span>';
    } else {
      docsEl.innerHTML = docs.map(d => `
        <div class="assure-doc-item">
          <div class="assure-doc-icon" style="background:${d.iconColor}18;">
            <span class="material-symbols-outlined" style="color:${d.iconColor};">${d.icon}</span>
          </div>
          <div class="assure-doc-info">
            <div class="assure-doc-name">${d.name}</div>
            <div class="assure-doc-meta">${d.type} · ${d.size} · ${d.date}</div>
          </div>
          <span class="assure-doc-status ${d.status}">${d.status === 'complete' ? 'Complet' : 'En attente'}</span>
        </div>
      `).join('');
    }
  }

  setText('assureAdvisorName', 'Jean Dupont');
  setText('assureAdvisorEmail', 'jean.dupont@previa.fr');
  setText('assureAdvisorPhone', '+33 1 42 86 XX XX');
  setText('assureAdvisorRef', client.clientRef);

  setText('assureDossierPolicy', client.policyNumber);
  setText('assureDossierType', client.contractTypeLabel);
  setText('assureDossierPremium', `${client.annualPremium.toLocaleString('fr-FR')} €/an`);
  setText('assureDossierExpiry', client.expiryDate);
}

/* ═══════════════════════════════════════════════════════════════
   SIGN MODAL
   ═══════════════════════════════════════════════════════════════ */

function setupSignModal(): void {
  const signBtn = document.getElementById('assureSignBtn');
  const modal = document.getElementById('assureSignModal');
  const closeBtn = document.getElementById('assureSignModalClose');
  const confirmBtn = document.getElementById('assureSignConfirm');

  if (signBtn && modal) {
    signBtn.addEventListener('click', () => {
      if (Array.from(state.selectedWorks).length === 0) return;
      populateSignModal();
      modal.classList.add('open');
    });
  }

  if (closeBtn && modal) {
    closeBtn.addEventListener('click', () => modal.classList.remove('open'));
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.classList.remove('open'); });
  }

  if (confirmBtn && modal) {
    confirmBtn.addEventListener('click', () => {
      state.engagementSigned = true;
      modal.classList.remove('open');

      setText('assureEngagementStatusLabel', 'Engagement signé');
      const pill = document.getElementById('assureEngagementPill');
      if (pill) {
        pill.className = 'assure-engagement-status signed';
        pill.innerHTML = '<span class="material-symbols-outlined" style="font-size:14px!important;">verified</span> Engagement signé';
      }

      renderBien();
    });
  }
}

function populateSignModal(): void {
  const works = Array.from(state.selectedWorks);
  const client = state.selectedClientId ? store.getClient(state.selectedClientId) : null;
  const savings = computeAnnualSavings(works);
  const annualPremium = getAnnualPremium();
  const newPremium = Math.max(0, annualPremium - savings);
  const cost = computeTotalCost(works);

  setText('assureModalPolRef', client?.policyNumber || '—');
  setText('assureModalClient', client ? `${client.civility} ${client.firstName} ${client.lastName}` : '—');
  setText('assureModalNewPremium', `${newPremium.toLocaleString('fr-FR')} € / an`);
  setText('assureModalSavings', `− ${savings.toLocaleString('fr-FR')} € / an`);
  setText('assureModalTotalCost', `${cost.toLocaleString('fr-FR')} €`);

  const expiry = new Date();
  expiry.setFullYear(expiry.getFullYear() + 10);
  setText('assureModalExpiry', expiry.toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' }));

  const worksEl = document.getElementById('assureModalWorks');
  if (worksEl) {
    const selected = Object.values(housePartData).filter(c => works.includes(c.id));
    worksEl.innerHTML = selected.map(c => `
      <div class="assure-avenant-works-item">
        <span class="material-symbols-outlined" style="color:#10b981;">check_circle</span>
        <span>${c.label}</span>
        <span style="margin-left:auto;font-size:11px;color:var(--text-muted);">${c.cost}</span>
      </div>
    `).join('');
  }
}

/* ═══════════════════════════════════════════════════════════════
   Utility
   ═══════════════════════════════════════════════════════════════ */

function getAnnualPremium(): number {
  if (state.selectedClientId) {
    const client = store.getClient(state.selectedClientId);
    if (client) return client.annualPremium;
  }
  return 1240;
}

/* ═══════════════════════════════════════════════════════════════
   CUSTOM DROPDOWN — Replaces native <select> with styled div dropdown
   ═══════════════════════════════════════════════════════════════ */

let customDropdownInitialized = false;

/** Initialize all custom dropdowns in the assured form */
function initCustomDropdowns(): void {
  if (customDropdownInitialized) return;
  customDropdownInitialized = true;

  document.querySelectorAll('.afi-select').forEach(select => {
    buildCustomDropdown(select as HTMLSelectElement);
  });
}

/** Build a custom dropdown from a native <select> */
function buildCustomDropdown(select: HTMLSelectElement): void {
  if (select.getAttribute('data-custom-dd')) return;
  select.setAttribute('data-custom-dd', 'true');

  const wrapper = document.createElement('div');
  wrapper.className = 'cdd-wrapper';

  // Trigger button — shows selected value
  const trigger = document.createElement('button');
  trigger.type = 'button';
  trigger.className = 'cdd-trigger';
  trigger.setAttribute('aria-haspopup', 'listbox');

  const triggerText = document.createElement('span');
  triggerText.className = 'cdd-trigger-text';
  triggerText.textContent = select.options[select.selectedIndex]?.text || 'Sélectionnez...';

  const triggerIcon = document.createElement('span');
  triggerIcon.className = 'material-symbols-outlined cdd-chevron';
  triggerIcon.textContent = 'expand_more';

  trigger.appendChild(triggerText);
  trigger.appendChild(triggerIcon);

  // Dropdown menu
  const menu = document.createElement('div');
  menu.className = 'cdd-menu';
  menu.setAttribute('role', 'listbox');

  // Build options
  Array.from(select.options).forEach((opt, index) => {
    const item = document.createElement('button');
    item.type = 'button';
    item.className = 'cdd-item';
    if (opt.selected) item.classList.add('selected');
    if (!opt.value) item.classList.add('placeholder');
    item.setAttribute('role', 'option');
    item.setAttribute('aria-selected', String(opt.selected));
    item.textContent = opt.text;

    item.addEventListener('click', () => {
      select.selectedIndex = index;
      // Update trigger text
      triggerText.textContent = opt.text;
      // Update selected state on all items
      menu.querySelectorAll('.cdd-item').forEach(el => {
        el.classList.remove('selected');
        el.setAttribute('aria-selected', 'false');
      });
      item.classList.add('selected');
      item.setAttribute('aria-selected', 'true');
      // Close menu
      menu.classList.remove('open');
      trigger.classList.remove('open');
      triggerIcon.textContent = 'expand_more';
      // Trigger change event on original select
      select.dispatchEvent(new Event('change', { bubbles: true }));
    });

    menu.appendChild(item);
  });

  // Toggle dropdown on trigger click
  trigger.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = menu.classList.toggle('open');
    trigger.classList.toggle('open', isOpen);
    triggerIcon.textContent = isOpen ? 'expand_less' : 'expand_more';
    if (isOpen) {
      // Position menu below trigger
      const rect = trigger.getBoundingClientRect();
      menu.style.top = rect.height + 4 + 'px';
      menu.style.left = '0';
      menu.style.width = '100%';
      // Scroll selected item into view
      const selected = menu.querySelector('.cdd-item.selected') as HTMLElement | null;
      if (selected) {
        setTimeout(() => selected.scrollIntoView({ block: 'nearest' }), 50);
      }
    }
  });

  wrapper.appendChild(trigger);
  wrapper.appendChild(menu);

  // Insert wrapper before select, hide select
  select.parentElement?.insertBefore(wrapper, select);
  select.style.display = 'none';

  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!wrapper.contains(e.target as Node)) {
      menu.classList.remove('open');
      trigger.classList.remove('open');
      triggerIcon.textContent = 'expand_more';
    }
  });
}

/* ═══════════════════════════════════════════════════════════════
   FORMULAIRE CLIENT — Form logic + Mode toggle
   ═══════════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════════
   DOCUMENT UPLOAD — Photo/plan/PDF upload zone logic
   ═══════════════════════════════════════════════════════════════ */

let uploadedFiles: File[] = [];

/** Initialize upload zone: drag-drop, file select, preview */
function initUploadZone(): void {
  const zone = document.getElementById('assureUploadZone');
  const input = document.getElementById('assureFileInput') as HTMLInputElement | null;
  const btn = zone?.querySelector('.assure-upload-btn') as HTMLElement | null;
  if (!zone || !input) return;

  // Click button → open file picker
  btn?.addEventListener('click', (e) => {
    e.stopPropagation();
    input.click();
  });

  // Click zone → open file picker
  zone.addEventListener('click', () => input.click());

  // File selected via picker
  input.addEventListener('change', () => {
    if (input.files) {
      addFiles(Array.from(input.files));
      input.value = '';
    }
  });

  // Drag events
  zone.addEventListener('dragover', (e) => {
    e.preventDefault();
    zone.classList.add('dragover');
  });

  zone.addEventListener('dragleave', () => {
    zone.classList.remove('dragover');
  });

  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('dragover');
    if (e.dataTransfer?.files) {
      addFiles(Array.from(e.dataTransfer.files));
    }
  });
}

/** Add files to the upload list */
function addFiles(files: File[]): void {
  const MAX_SIZE = 20 * 1024 * 1024; // 20 MB
  const validFiles = files.filter(f => f.size <= MAX_SIZE);

  if (validFiles.length !== files.length) {
    showError('❌ Certains fichiers dépassent la limite de 20 Mo et ont été ignorés.');
  }

  uploadedFiles = [...uploadedFiles, ...validFiles];
  renderUploadList();
}

/** Render the upload file list with previews */
function renderUploadList(): void {
  const list = document.getElementById('assureUploadList');
  const zone = document.getElementById('assureUploadZone');
  if (!list || !zone) return;

  if (uploadedFiles.length === 0) {
    list.style.display = 'none';
    zone.classList.remove('has-files');
    return;
  }

  list.style.display = 'flex';
  zone.classList.add('has-files');

  list.innerHTML = uploadedFiles.map((file, index) => {
    const isImage = file.type.startsWith('image/');
    const sizeStr = formatFileSize(file.size);
    const icon = isImage ? '' : getDocIcon(file.name);
    const preview = isImage ? `<img src="${URL.createObjectURL(file)}" alt="${file.name}">` : `<span class="material-symbols-outlined">${icon}</span>`;

    return `
      <div class="upload-item">
        <div class="upload-item-icon">${preview}</div>
        <div class="upload-item-info">
          <div class="upload-item-name">${escapeHtml(file.name)}</div>
          <div class="upload-item-size">${sizeStr}</div>
        </div>
        <button type="button" class="upload-item-remove" data-index="${index}">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>
    `;
  }).join('');

  // Remove buttons
  list.querySelectorAll('.upload-item-remove').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const idx = parseInt((e.currentTarget as HTMLElement).getAttribute('data-index') || '0', 10);
      uploadedFiles.splice(idx, 1);
      renderUploadList();
    });
  });
}

/** Get Material Icon for document type */
function getDocIcon(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase() || '';
  const icons: Record<string, string> = {
    pdf: 'picture_as_pdf',
    dwg: 'draw',
    dxf: 'draw',
    doc: 'description',
    docx: 'description',
    xls: 'table_chart',
    xlsx: 'table_chart',
  };
  return icons[ext] || 'insert_drive_file';
}

/** Format file size */
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' o';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' Ko';
  return (bytes / (1024 * 1024)).toFixed(1) + ' Mo';
}

/** Simple HTML escaping */
function escapeHtml(str: string): string {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/** Collect all form field values */
function collectFormData(): Record<string, any> {
  const getVal = (id: string) => (document.getElementById(id) as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement)?.value || '';
  const getCheck = (id: string) => (document.getElementById(id) as HTMLInputElement)?.checked || false;

  return {
    address: getVal('afi_address'),
    postalCode: getVal('afi_postalCode'),
    city: getVal('afi_city'),
    typeBien: getVal('afi_typeBien'),
    surface: parseFloat(getVal('afi_surface')) || undefined,
    nbPieces: parseInt(getVal('afi_nbPieces')) || undefined,
    nbEtages: parseInt(getVal('afi_nbEtages')) || undefined,
    anneeConstruction: parseInt(getVal('afi_anneeConstruction')) || undefined,
    anneeRenovation: parseInt(getVal('afi_anneeRenovation')) || undefined,
    capitalAssure: parseFloat(getVal('afi_capitalAssure')) || undefined,
    typeStructure: getVal('afi_typeStructure') || undefined,
    etatStructure: getVal('afi_etatStructure') || undefined,
    fissures: getVal('afi_fissures') || undefined,
    affaissement: getVal('afi_affaissement') || undefined,
    typeToiture: getVal('afi_typeToiture') || undefined,
    ageToiture: parseInt(getVal('afi_ageToiture')) || undefined,
    anneeToiture: parseInt(getVal('afi_anneeToiture')) || undefined,
    etatToiture: getVal('afi_etatToiture') || undefined,
    isolationToiture: getVal('afi_isolationToiture') || undefined,
    isolationMurs: getVal('afi_isolationMurs') || undefined,
    isolationSol: getVal('afi_isolationSol') || undefined,
    infiltrations: getVal('afi_infiltrations') || undefined,
    presenceSousSol: getCheck('afi_presenceSousSol'),
    presenceCave: getCheck('afi_presenceCave'),
    presenceGarage: getCheck('afi_presenceGarage'),
    occupation: getVal('afi_occupation') || undefined,
    climatisation: getCheck('afi_climatisation'),
    chauffagePrincipal: getVal('afi_chauffagePrincipal') || undefined,
    installationElectriqueAnnee: parseInt(getVal('afi_installationElectriqueAnnee')) || undefined,
    presenceDetecteursFumee: getCheck('afi_presenceDetecteursFumee'),
    expositionSolaire: getVal('afi_expositionSolaire') || undefined,
    zoneMitoyennete: getVal('afi_zoneMitoyennete') || undefined,
    dpeClass: getVal('afi_dpeClass') || undefined,
    observations: getVal('afi_observations') || undefined,
    hauteurPlancher: parseFloat(getVal('afi_hauteurPlancher')) || undefined,
    clapetAntiRetour: getCheck('afi_clapetAntiRetour'),
    equipementsElecSousSol: getCheck('afi_equipementsElecSousSol'),
    profondeurFondations: getVal('afi_profondeurFondations') || undefined,
    arbresProches: getCheck('afi_arbresProches'),
    materiauToit: getVal('afi_materiauToit') || undefined,
    panneauxSolaires: getCheck('afi_panneauxSolaires'),
  };
}

/** Setup wizard navigation (next/prev) and form submission */
function setupPropertyForm(): void {
  const form = document.getElementById('assurePropertyForm') as HTMLFormElement | null;
  if (!form) return;

  // Next buttons
  form.querySelectorAll('.assure-btn-next').forEach(btn => {
    btn.addEventListener('click', () => {
      const next = parseInt((btn as HTMLElement).getAttribute('data-next') || '0');
      goToStep(next);
    });
  });

  // Previous buttons
  form.querySelectorAll('[data-prev]').forEach(btn => {
    btn.addEventListener('click', () => {
      const prev = parseInt((btn as HTMLElement).getAttribute('data-prev') || '0');
      goToStep(prev);
    });
  });

  // Submit
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = document.getElementById('assureFormSubmitBtn') as HTMLButtonElement | null;
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="material-symbols-outlined" style="animation:spin 1s linear infinite;">refresh</span> Enregistrement...';
    }

    const formData = collectFormData();
    // Fallback: try to get or create a client if none selected
    let clientId = state.selectedClientId;
    if (!clientId) {
      try {
        const session = await fetch('/api/auth/session').then(r => r.ok ? r.json() : null);
        const userId = session?.user?.id || session?.sub || 'demo-user';
        // Try to find existing client for this user, or create one
        let clientRes = await fetch(`/api/clients?userId=${userId}`).then(r => r.ok ? r.json() : []);
        if (clientRes.length > 0) {
          clientId = clientRes[0].id;
          state.selectedClientId = clientId;
        } else {
          // Create a default client
          clientRes = await fetch('/api/clients', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ userId, firstName: 'Client', lastName: 'Prévia', email: '' }),
          }).then(r => r.ok ? r.json() : null);
          clientId = clientRes?.id || 'demo-client';
          state.selectedClientId = clientId;
        }
      } catch {
        clientId = 'demo-client';
        state.selectedClientId = clientId;
      }
    }

    try {
      const res = await fetch('/api/properties/input', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, clientId }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.message || `HTTP ${res.status}`);
      }

      const saved = await res.json();
      localStorage.setItem('assure_form_completed', '1');
      localStorage.setItem('assure_form_data', JSON.stringify(formData));
      localStorage.setItem('assure_property_id', saved.id);

      showSuccess('✅ Bien enregistré avec succès !');

      // Switch to dashboard mode
      const formView = document.getElementById('assureFormView');
      const dashView = document.getElementById('assureDashView');
      const modeSelector = document.getElementById('assureModeSelector');
      if (formView && dashView && modeSelector) {
        formView.style.display = 'none';
        dashView.style.display = '';
        modeSelector.style.display = 'flex';
        document.querySelectorAll('.assure-mode-btn').forEach(b => b.classList.remove('active'));
        document.getElementById('assureModeDashBtn')?.classList.add('active');
        loadPropertyDataIntoDashboard();
        renderBien();
      }
    } catch (err: any) {
      showError('❌ Erreur : ' + (err.message || 'Impossible de sauvegarder'));
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span class="material-symbols-outlined">save</span> Enregistrer mon bien';
      }
    }
  });
}

function goToStep(step: number): void {
  // Update panels
  document.querySelectorAll('.afs-panel').forEach(p => p.classList.remove('active'));
  const target = document.querySelector(`.afs-panel[data-step="${step}"]`);
  if (target) target.classList.add('active');

  // Update steps indicator
  document.querySelectorAll('.afs-step').forEach(s => {
    const sStep = parseInt((s as HTMLElement).getAttribute('data-step') || '0');
    s.classList.toggle('active', sStep === step);
    s.classList.toggle('completed', sStep < step);
  });

  // Populate recap summary when reaching step 5
  if (step === 5) {
    populateFormSummary();
  }

  // Scroll to top of form
  const container = document.querySelector('.assure-form-container');
  if (container) container.scrollTop = 0;
}

/* ═══════════════════════════════════════════════════════════════
   FORM SUMMARY — Recap all collected data before submit
   ═══════════════════════════════════════════════════════════════ */

/** Get text value of a select/input, or a human-readable label from a select */
function getLabel(id: string): string {
  const el = document.getElementById(id) as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement | null;
  if (!el) return '—';
  const val = el.value?.trim();
  if (!val) return '—';
  // For select elements, try to get the selected option text
  if (el instanceof HTMLSelectElement && el.selectedIndex >= 0) {
    return el.options[el.selectedIndex]?.text || val;
  }
  return val;
}

/** Get checkbox state as Oui/Non */
function getCheckLabel(id: string): string {
  const el = document.getElementById(id) as HTMLInputElement | null;
  if (!el) return 'Non';
  return el.checked ? 'Oui' : 'Non';
}

/** Set text content of a summary element */
function setSummary(id: string, value: string): void {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

/** Populate the recap summary section in step 5 */
function populateFormSummary(): void {
  // Section 1 — Localisation
  setSummary('summaryAddress', getLabel('afi_address'));
  setSummary('summaryPostalCode', getLabel('afi_postalCode'));
  setSummary('summaryCity', getLabel('afi_city'));
  setSummary('summaryTypeBien', getLabel('afi_typeBien'));
  setSummary('summarySurface', getLabel('afi_surface'));
  setSummary('summaryPieces', getLabel('afi_nbPieces'));
  setSummary('summaryEtages', getLabel('afi_nbEtages'));

  // Section 2 — Structure
  setSummary('summaryAnneeConst', getLabel('afi_anneeConstruction'));
  setSummary('summaryAnneeRenov', getLabel('afi_anneeRenovation'));
  setSummary('summaryStructure', getLabel('afi_typeStructure'));
  setSummary('summaryEtatStructure', getLabel('afi_etatStructure'));
  setSummary('summaryFissures', getLabel('afi_fissures'));
  setSummary('summaryAffaissement', getLabel('afi_affaissement'));
  setSummary('summaryFondations', getLabel('afi_profondeurFondations'));
  setSummary('summaryHauteur', getLabel('afi_hauteurPlancher'));

  // Section 3 — Toiture & Isolation
  setSummary('summaryTypeToiture', getLabel('afi_typeToiture'));
  setSummary('summaryMateriauToit', getLabel('afi_materiauToit'));
  setSummary('summaryAgeToiture', getLabel('afi_ageToiture'));
  setSummary('summaryAnneeToiture', getLabel('afi_anneeToiture'));
  setSummary('summaryEtatToiture', getLabel('afi_etatToiture'));
  setSummary('summaryIsolToiture', getLabel('afi_isolationToiture'));
  setSummary('summaryIsolMurs', getLabel('afi_isolationMurs'));
  setSummary('summaryIsolSol', getLabel('afi_isolationSol'));
  setSummary('summaryPanneaux', getCheckLabel('afi_panneauxSolaires'));

  // Section 4 — Équipements
  setSummary('summaryChauffage', getLabel('afi_chauffagePrincipal'));
  setSummary('summaryElectrique', getLabel('afi_installationElectriqueAnnee'));
  setSummary('summaryClim', getCheckLabel('afi_climatisation'));
  setSummary('summaryDetecteurs', getCheckLabel('afi_presenceDetecteursFumee'));
  setSummary('summaryOccupation', getLabel('afi_occupation'));
  setSummary('summaryInfiltrations', getLabel('afi_infiltrations'));
  setSummary('summarySousSol', getCheckLabel('afi_presenceSousSol'));
  setSummary('summaryCave', getCheckLabel('afi_presenceCave'));
  setSummary('summaryGarage', getCheckLabel('afi_presenceGarage'));
  setSummary('summaryArbres', getCheckLabel('afi_arbresProches'));

  // Section 5 — Finalisation fields
  setSummary('summaryDpe', getLabel('afi_dpeClass'));
  setSummary('summaryExposition', getLabel('afi_expositionSolaire'));
  setSummary('summaryMitoyennete', getLabel('afi_zoneMitoyennete'));
  setSummary('summaryCapital', getLabel('afi_capitalAssure'));
}

/** Setup mode toggle (form vs dashboard) */
function setupModeToggle(): void {
  const formBtn = document.getElementById('assureModeFormBtn');
  const dashBtn = document.getElementById('assureModeDashBtn');
  const formView = document.getElementById('assureFormView');
  const dashView = document.getElementById('assureDashView');

  formBtn?.addEventListener('click', () => {
    if (!formView || !dashView) return;
    formView.style.display = '';
    dashView.style.display = 'none';
    formBtn.classList.add('active');
    dashBtn?.classList.remove('active');
  });

  dashBtn?.addEventListener('click', () => {
    if (!formView || !dashView) return;
    formView.style.display = 'none';
    dashView.style.display = '';
    dashBtn.classList.add('active');
    formBtn?.classList.remove('active');
    loadPropertyDataIntoDashboard();
    renderBien();
  });
}

/** Load saved form data into dashboard fields */
function loadPropertyDataIntoDashboard(): void {
  const data = localStorage.getItem('assure_form_data');
  if (!data) return;
  try {
    const formData = JSON.parse(data);
    const set = (id: string, val: string) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val || '—';
    };
    set('assurePropAddress', formData.address || '—');
    set('assurePropCity', formData.city || '—');
    set('assurePropDpe', formData.dpeClass || '—');
    set('assurePropYear', formData.anneeConstruction ? String(formData.anneeConstruction) : '—');
    set('assureBannerAddress', (formData.address || '') + (formData.city ? ', ' + formData.city : ''));

    // Use property ID to link to the assureur's Risk Hub
    const propId = localStorage.getItem('assure_property_id');
    const linkEl = document.getElementById('assurePropRiskLink');
    if (linkEl && propId) {
      linkEl.setAttribute('href', `/assureur/risk-hub?propertyId=${propId}`);
      linkEl.style.display = 'inline-flex';
    }

    // Compute a mock score from form data richness
    const filledCount = Object.values(formData).filter(v => v !== undefined && v !== '' && v !== false).length;
    const mockScore = Math.min(95, 30 + filledCount * 2);
    set('assureBannerScore', String(mockScore));
    set('assureStatScore', String(mockScore));
    set('assurePropScore', mockScore + '%');
  } catch {}
}

/** Toast notifications */
function showSuccess(msg: string): void {
  const toast = document.createElement('div');
  toast.className = 'assure-toast';
  toast.innerHTML = msg;
  toast.style.cssText = 'position:fixed;bottom:24px;right:24px;background:#059669;color:#fff;padding:12px 20px;border-radius:8px;font-size:13px;z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,0.15);animation:slideUp 0.3s ease;';
  document.body.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; setTimeout(() => toast.remove(), 300); }, 3000);
}

function showError(msg: string): void {
  const toast = document.createElement('div');
  toast.className = 'assure-toast';
  toast.innerHTML = msg;
  toast.style.cssText = 'position:fixed;bottom:24px;right:24px;background:#dc2626;color:#fff;padding:12px 20px;border-radius:8px;font-size:13px;z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,0.15);animation:slideUp 0.3s ease;';
  document.body.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; setTimeout(() => toast.remove(), 300); }, 5000);
}
