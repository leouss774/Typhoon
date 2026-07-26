/**
 * Expert Form — 15-field questionnaire + actuarial computation
 * ============================================================
 * 
 * Handles the "Calculer les Risques Actuariels" form submission,
 * deterministic contributors computation, AI narrative generation,
 * pricing signal updates, demo fill, and underwriting controls.
 */

import { RiskState } from './risk-state.js';
import { triggerEvaluateRefresh } from './risk-utils.js';

// ── Local helpers (avoids circular dependency with property-risk.ts) ──

function showToast(html: string, durationMs: number = 4000): void {
  let container = document.getElementById('riskToastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'riskToastContainer';
    container.className = 'risk-toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = 'risk-toast';
  toast.innerHTML = html;
  container.appendChild(toast);
  setTimeout(() => {
    if (toast.parentNode) {
      toast.classList.add('removing');
      setTimeout(() => { if (toast.parentNode) toast.remove(); }, 250);
    }
  }, durationMs);
}

function navigateToTab(tabKey: string): void {
  // Delegate to property-risk.ts via custom event — it handles panel switching,
  // step indicators, URL updates, 3D init, and map lifecycle
  window.dispatchEvent(new CustomEvent('previa:nav', { detail: { tab: tabKey } }));
}

/* ═══════════════════════════════════════════════════════════════
   Public API
   ═══════════════════════════════════════════════════════════════ */

export function setupDemoFill(): void {
  const demoBtn = document.getElementById('riskDemoFillBtn');
  if (!demoBtn) return;

  demoBtn.addEventListener('click', () => {
    const setSelect = (id: string, val: string) => {
      const el = document.getElementById(id) as HTMLSelectElement | null;
      if (el) {
        el.value = val;
        // Dispatch change event so custom dropdowns sync
        el.dispatchEvent(new Event('change', { bubbles: true }));
      }
    };
    const setInput = (id: string, val: string) => {
      const el = document.getElementById(id) as HTMLInputElement | null;
      if (el) el.value = val;
    };

    setSelect('expertTypeBien', 'individuelle');
    setInput('expertNbPieces', '5');
    setSelect('expertSousSol', 'oui');
    setInput('expertCapitalAssure', '250000');
    setInput('expertHauteurPlancher', '30');
    setSelect('expertClapet', 'non');
    setSelect('expertEquipElec', 'non');
    setSelect('expertZoneInondable', 'moyen');
    setSelect('expertProfFondations', 'moins50');
    setSelect('expertFissures', 'legeres');
    setSelect('expertArbres', 'oui');
    setSelect('expertCave', 'oui');
    setInput('expertAgeToiture', '15');
    setSelect('expertMateriauToit', 'tuiles');
    setSelect('expertPanneauxSolaires', 'non');

    if (!RiskState.getScores()) {
      RiskState.setScores({
        inondation: 52, rga: 45, tempete: 38,
        incendie: 12, seisme: 8, global: 36,
      });
    }

    navigateToTab('actuariat');
    showToast('<div class="risk-toast-body">⚡ Données démo pré-remplies</div>', 3000);
  });
}

export function setupExpertForm(): void {
  const calcBtn = document.getElementById('riskExpertCalcBtn');
  if (!calcBtn) return;

  // Photo scan mock click
  const photoScan = document.getElementById('expertPhotoScan');
  const photoInput = photoScan?.querySelector('input[type="file"]') as HTMLInputElement | null;
  if (photoScan && photoInput) {
    photoScan.addEventListener('click', (e) => {
      e.stopPropagation();
      photoInput.click();
    });
    photoInput.addEventListener('change', () => {
      if (photoInput.files?.length) {
        photoScan.innerHTML = `<span class="material-symbols-outlined">check_circle</span><span>Photo ajoutée</span>`;
        photoScan.style.borderColor = '#10b981';
      }
    });
  }

  calcBtn.addEventListener('click', () => {
    const getVal = (id: string): string =>
      (document.getElementById(id) as HTMLInputElement | HTMLSelectElement)?.value || '';

    const formData: Record<string, string> = {
      type_bien: getVal('expertTypeBien'),
      nb_pieces: getVal('expertNbPieces'),
      sous_sol: getVal('expertSousSol'),
      capital_assure: getVal('expertCapitalAssure'),
      hauteur_plancher: getVal('expertHauteurPlancher'),
      clapet: getVal('expertClapet'),
      equip_elec: getVal('expertEquipElec'),
      zone_inondable: getVal('expertZoneInondable'),
      prof_fondations: getVal('expertProfFondations'),
      fissures: getVal('expertFissures'),
      arbres: getVal('expertArbres'),
      cave: getVal('expertCave'),
      age_toiture: getVal('expertAgeToiture'),
      materiau_toit: getVal('expertMateriauToit'),
      panneaux: getVal('expertPanneauxSolaires'),
    };

    computeActuarialRisk(formData);
    
    // Save expert form to backend and advance status to en_expertise
    const assessment = RiskState.getAssessment() as any;
    if (assessment?.assessmentId) {
      import('../../api/assessments.js').then(({ saveExpertForm }) => {
        saveExpertForm(assessment.assessmentId, formData).catch((err) => console.error('Failed to save expert form:', err));
      });
    }

    navigateToTab('inspect');
    showToast('<div class="risk-toast-body">✅ Calcul actuariel terminé — Redirection vers l\'Inspection 3D</div>', 3000);
  });
}

/* ═══════════════════════════════════════════════════════════════
   Underwriting Controls
   ═══════════════════════════════════════════════════════════════ */

export function setupUwControls(): void {
  // Pricing signal status buttons
  document.querySelectorAll('.risk-uw-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.risk-uw-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const signal = btn.getAttribute('data-signal') || 'STANDARD';
      updatePricingSignalLabel(signal);
    });
  });

  // Score override
  const overrideEl = document.getElementById('riskUwScoreOverride') as HTMLSelectElement | null;
  overrideEl?.addEventListener('change', () => {
    const scores = RiskState.getScores();
    if (!scores) return;
    const override = parseInt(overrideEl.value) || 0;
    const adjusted = Math.min(100, Math.max(0, scores.global + override));
    updatePricingSignal(adjusted);
  });

  // PDF Export
  const approveBtn = document.getElementById('riskUwApprove');
  approveBtn?.addEventListener('click', () => {
    const rationale = (document.getElementById('riskUwRationale') as HTMLTextAreaElement)?.value || '';
    const scores = RiskState.getScores();
    const signalEl = document.getElementById('riskSignalLabel');
    const signal = signalEl?.textContent || 'STANDARD';

    const pdfContent = `
PRÉVIA — Avenant d'Assurance Habitation
========================================
Signal de tarification: ${signal}
Score global: ${scores?.global ?? 'N/A'}/100
Justification souscripteur: ${rationale || '(aucune)'}
Date: ${new Date().toLocaleDateString('fr-FR')}
----------------------------------------
Document généré le ${new Date().toISOString()}
    `.trim();

    // Create a downloadable text file as PDF mock
    const blob = new Blob([pdfContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `avenant-previa-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);

    showToast('<div class="risk-toast-body">📄 Avenant exporté (format texte)</div>', 3000);
  });
}

/* ═══════════════════════════════════════════════════════════════
   Actuarial Computation
   ═══════════════════════════════════════════════════════════════ */

export function computeActuarialRisk(formData: Record<string, string>): void {
  const contributors: Array<{ name: string; source: string; points: number }> = [];

  // Inondation
  const hauteur = parseInt(formData.hauteur_plancher) || 30;
  contributors.push({
    name: hauteur < 50 ? 'Hauteur plancher < 50 cm' : 'Hauteur plancher > 50 cm',
    source: 'Donnée déclarative',
    points: hauteur < 50 ? +8 : -5,
  });
  contributors.push({
    name: formData.clapet === 'non' ? 'Absence clapet anti-retour' : 'Clapet anti-retour présent',
    source: 'Donnée déclarative',
    points: formData.clapet === 'non' ? +10 : -10,
  });
  if (formData.zone_inondable !== 'none') {
    const zonePoints: Record<string, number> = { faible: +5, moyen: +12, fort: +20 };
    contributors.push({
      name: `Zone inondable: ${formData.zone_inondable}`,
      source: 'PPRI / Géorisques',
      points: zonePoints[formData.zone_inondable] || 0,
    });
  }

  // RGA
  const prof = formData.prof_fondations;
  contributors.push({
    name: prof === 'moins50' ? 'Fondations < 50 cm' : prof === '50a80' ? 'Fondations 50-80 cm' : 'Fondations > 80 cm',
    source: 'Règles métier',
    points: prof === 'moins50' ? +12 : prof === '50a80' ? +6 : -8,
  });
  if (formData.fissures === 'importantes') contributors.push({ name: 'Fissures importantes', source: 'Donnée déclarative', points: +15 });
  else if (formData.fissures === 'legeres') contributors.push({ name: 'Fissures légères', source: 'Donnée déclarative', points: +5 });
  if (formData.arbres === 'oui') contributors.push({ name: 'Arbres à < 5 m', source: 'Donnée déclarative', points: +8 });

  // Tempête
  const ageToit = parseInt(formData.age_toiture) || 15;
  if (ageToit > 20) contributors.push({ name: 'Toiture > 20 ans', source: 'Donnée déclarative', points: +10 });
  else if (ageToit > 10) contributors.push({ name: 'Toiture 10-20 ans', source: 'Donnée déclarative', points: +4 });
  else contributors.push({ name: 'Toiture récente < 10 ans', source: 'Donnée déclarative', points: -6 });
  if (formData.materiau_toit === 'tole') contributors.push({ name: 'Matériau toit: bac acier', source: 'Donnée déclarative', points: +6 });
  if (formData.panneaux === 'oui') contributors.push({ name: 'Panneaux solaires', source: 'Donnée déclarative', points: +4 });

  // Compute base scores from contributors
  let inondationScore = 40, rgaScore = 30, tempeteScore = 25;
  for (const c of contributors) {
    const n = c.name.toLowerCase();
    if (n.includes('plancher') || n.includes('clapet') || n.includes('inondable')) inondationScore += c.points * 0.6;
    if (n.includes('fondation') || n.includes('fissure') || n.includes('arbre')) rgaScore += c.points * 0.6;
    if (n.includes('toiture') || n.includes('toit') || n.includes('panneau') || n.includes('bac')) tempeteScore += c.points * 0.6;
  }

  const scores = {
    inondation: Math.min(100, Math.max(0, Math.round(inondationScore))),
    rga: Math.min(100, Math.max(0, Math.round(rgaScore))),
    tempete: Math.min(100, Math.max(0, Math.round(tempeteScore))),
    incendie: 10,
    seisme: 5,
    global: 0,
  };
  scores.global = Math.round(
    scores.inondation * 0.30 + scores.rga * 0.25 + scores.tempete * 0.20 + scores.incendie * 0.15 + scores.seisme * 0.10
  );

  RiskState.setScores(scores);
  renderDeterministicContributors(contributors);
  renderAiNarrative(scores, contributors);
  updatePricingSignal(scores.global);
  triggerEvaluateRefresh();
}

/* ═══════════════════════════════════════════════════════════════
   Renderers
   ═══════════════════════════════════════════════════════════════ */

function renderDeterministicContributors(contributors: Array<{ name: string; source: string; points: number }>): void {
  const grid = document.getElementById('riskContributorsGrid');
  if (!grid) return;
  grid.innerHTML = contributors.map(c => `
    <div class="risk-contributor-card">
      <div class="risk-contributor-info">
        <span class="risk-contributor-name">${c.name}</span>
        <span class="risk-contributor-source">${c.source}</span>
      </div>
      <span class="risk-contributor-points ${c.points >= 0 ? 'positive' : 'negative'}">${c.points >= 0 ? '+' : ''}${c.points} pts</span>
    </div>
  `).join('');
}

function renderAiNarrative(scores: Record<string, number>, contributors: Array<{ name: string; points: number }>): void {
  const narrativeEl = document.getElementById('riskAiNarrative');
  const badgeEl = document.getElementById('riskAiBadge');
  if (!narrativeEl) return;
  if (badgeEl) badgeEl.style.display = 'inline-flex';

  const topRisks = contributors.filter(c => c.points >= 8).map(c => c.name.toLowerCase()).slice(0, 3);
  const mitigations = contributors.filter(c => c.points < 0).map(c => c.name).slice(0, 2);

  const fullText = `Analyse des risques pour ce bien :

Le score global de ${scores.global}/100 reflète une exposition ${scores.global < 30 ? 'faible' : scores.global < 50 ? 'modérée' : scores.global < 70 ? 'élevée' : 'critique'} aux aléas naturels. ${topRisks.length ? 'Les principaux facteurs de risque sont : ' + topRisks.join(', ') + '.' : 'Aucun facteur de risque majeur identifié.'}

Décomposition par péril :
• Inondation : ${scores.inondation}/100
• Retrait-gonflement argiles : ${scores.rga}/100
• Tempête : ${scores.tempete}/100
• Incendie : ${scores.incendie}/100
• Séisme : ${scores.seisme}/100

${mitigations.length ? 'Points forts : ' + mitigations.map(m => m + ' (-' + contributors.find(c => c.name === m)?.points + ' pts)').join(', ') : ''}

Recommandation : ${scores.global < 30 ? 'Profil favorable. Souscription recommandée aux conditions standard.' : scores.global < 50 ? 'Risque modéré. Des travaux de mitigation pourraient améliorer le score.' : scores.global < 70 ? 'Risque élevé. Une expertise complémentaire est recommandée avant souscription.' : 'Risque critique. Déconseillé sans travaux préalables de mise en sécurité.'}`;

  // Check if assessment ID is available to trigger real Mistral call
  const assessment = RiskState.getAssessment() as any;
  if (assessment?.assessmentId) {
    narrativeEl.innerHTML = '<p class="risk-ai-placeholder"><span class="material-symbols-outlined" style="animation:spin 1s linear infinite;">refresh</span> Génération du rapport via Mistral AI…</p>';
    
    import('../../api/assessments.js').then(({ generateEvaluationReport }) => {
      generateEvaluationReport(assessment.assessmentId, {
        global: scores.global,
        inondation: scores.inondation,
        rga: scores.rga,
        tempete: scores.tempete,
        incendie: scores.incendie,
        seisme: scores.seisme,
      }).then((res) => {
        if (badgeEl) badgeEl.style.display = 'none';
        const r = res.report;
        narrativeEl.innerHTML = `
          <div style="font-size:12px;line-height:1.5;">
            <p style="margin-bottom:8px;font-weight:600;color:var(--color-primary);">${r.resume}</p>
            <p style="margin-bottom:8px;">${r.syntheseTexte.replace(/\n/g, '<br>')}</p>
            <div style="margin-top:8px;padding-top:8px;border-top:1px solid var(--border-color);">
              <span style="font-weight:600;font-size:11px;">Points de vigilance :</span>
              <ul style="margin:4px 0 8px 16px;padding:0;">
                ${r.pointsVigilance.map((p: string) => `<li>${p}</li>`).join('')}
              </ul>
            </div>
          </div>
        `;
      }).catch((err) => {
        console.error('Mistral generation error:', err);
        fallbackStream();
      });
    }).catch(fallbackStream);
  } else {
    fallbackStream();
  }

  function fallbackStream() {
    if (!narrativeEl) return;
    narrativeEl.innerHTML = '<p class="risk-ai-placeholder">Génération de l\'analyse IA</p><span class="risk-ai-cursor"></span>';
    let charIdx = 0;
    const streamInterval = setInterval(() => {
      if (charIdx >= fullText.length) {
        clearInterval(streamInterval);
        if (badgeEl) badgeEl.style.display = 'none';
        return;
      }
      charIdx = Math.min(charIdx + 25, fullText.length);
      const formatted = fullText.substring(0, charIdx).replace(/\n/g, '<br>');
      if (narrativeEl) narrativeEl.innerHTML = `<p style="margin:0;">${formatted}</p><span class="risk-ai-cursor"></span>`;
    }, 25);
  }
}

function updatePricingSignal(globalScore: number): void {
  const signalEl = document.getElementById('riskPricingSignal');
  const labelEl = document.getElementById('riskSignalLabel');
  if (!signalEl || !labelEl) return;

  let cls: string, icon: string, label: string;
  if (globalScore <= 30) { cls = 'favorable'; icon = '🟢'; label = 'FAVORABLE'; }
  else if (globalScore <= 50) { cls = 'standard'; icon = '🟡'; label = 'STANDARD'; }
  else if (globalScore <= 70) { cls = 'surcharge'; icon = '🟠'; label = 'SURCHARGE'; }
  else { cls = 'decliner'; icon = '🔴'; label = 'DÉCLINER'; }

  signalEl.className = `risk-pricing-signal ${cls}`;
  const iconEl = signalEl.querySelector('.risk-pricing-signal-icon');
  if (iconEl) iconEl.textContent = icon;
  labelEl.textContent = label;
  const subEl = signalEl.querySelector('.risk-pricing-signal-sub');
  if (subEl) subEl.textContent = `Score global: ${globalScore}/100`;
}

function updatePricingSignalLabel(signal: string): void {
  const signalEl = document.getElementById('riskPricingSignal');
  const labelEl = document.getElementById('riskSignalLabel');
  if (!signalEl || !labelEl) return;

  const map: Record<string, { cls: string; icon: string }> = {
    FAVORABLE: { cls: 'favorable', icon: '🟢' },
    STANDARD: { cls: 'standard', icon: '🟡' },
    SURCHARGE: { cls: 'surcharge', icon: '🟠' },
    DECLINER: { cls: 'decliner', icon: '🔴' },
  };
  const s = map[signal] || map.STANDARD;
  signalEl.className = `risk-pricing-signal ${s.cls}`;
  const iconEl = signalEl.querySelector('.risk-pricing-signal-icon');
  if (iconEl) iconEl.textContent = s.icon;
  labelEl.textContent = signal;
}
