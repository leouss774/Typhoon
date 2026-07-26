/**
 * Clients view module — table search, client wizard, contract/document UI.
 * Data loaded from API via data-service.ts with fallback to mock DataStore.
 */

import { fetchClientsFromApi, getCachedClients, getCachedClient } from '../../api/data-service.js';
import { showPrompt, showSuccess, showError, showInfo } from '../../utils/notifications.js';

let initialized = false;

/* ── Local state ────────────────────────────────────── */

let currentClientId: string | null = null;
let isEditing = false;

/* ── Lifecycle ──────────────────────────────────────── */

export function initClients(): void {
  if (initialized) return;
  initialized = true;
  loadClientsIntoTable();
  setupClientSearch();
  setupClientWizard();
  setupStaticActions();
}

export function destroyClients(): void {
  initialized = false;
}

/* ── Load client data from API → populate table ────── */

async function loadClientsIntoTable(): Promise<void> {
  try {
    const clients = await fetchClientsFromApi();
    const tbody = document.getElementById('clientsTableBody');
    if (!tbody) return;

    tbody.innerHTML = clients.map(c => {
      const initials = (c.firstName?.[0] || '') + (c.lastName?.[0] || '');
      const statusLabel: Record<string, string> = { active: 'Actif', pending: 'En attente', suspended: 'Suspendu' };
      return `
      <tr class="clients-table-row" data-client="${c.id}">
        <td><span class="clients-table-avatar">${initials}</span></td>
        <td><span class="clients-table-civ">${c.civility || ''}</span></td>
        <td class="clients-table-name">${c.firstName} ${c.lastName}</td>
        <td class="clients-table-email">${c.email || '—'}</td>
        <td>${c.phone || '—'}</td>
        <td>${c.insuredCity || '—'}</td>
        <td><span class="clients-table-status ${c.status || 'pending'}">${statusLabel[c.status as keyof typeof statusLabel] || c.status}</span></td>
        <td>
          <div class="clients-table-actions">
            <button class="clients-action-btn" data-action="view" title="Voir le détail"><span class="material-symbols-outlined">visibility</span></button>
            <button class="clients-action-btn" data-action="edit" title="Modifier"><span class="material-symbols-outlined">edit</span></button>
            <button class="clients-action-btn" data-action="status" title="Changer le statut"><span class="material-symbols-outlined">checklist</span></button>
            <button class="clients-action-btn" data-action="more" title="Plus d'options"><span class="material-symbols-outlined">more_horiz</span></button>
          </div>
        </td>
      </tr>`;
    }).join('');

    // Use event delegation on tbody for table clicks (no need to re-wire each row)
    wireTableDelegation(tbody);
  } catch (err) {
    console.warn('[Clients] Failed to load clients from API:', err);
  }
}

/* ── Client Search ──────────────────────────────────── */

function setupClientSearch(): void {
  const clientsSearch = document.getElementById('clientsSearch') as HTMLInputElement | null;
  if (!clientsSearch) return;

  clientsSearch.addEventListener('input', () => {
    const query = clientsSearch.value.toLowerCase().trim();
    const rows = document.querySelectorAll('#clientsTableBody .clients-table-row');
    rows.forEach(row => {
      const text = row.textContent?.toLowerCase() || '';
      (row as HTMLElement).style.display = !query || text.includes(query) ? '' : 'none';
    });
  });
}

/* ── Client Wizard ──────────────────────────────────── */

function setupClientWizard(): void {
  const modal = document.getElementById('clientWizardModal');
  const closeBtn = document.getElementById('wizardClose');
  const addBtn = document.getElementById('clientsAddBtn');
  const submitBtn = document.getElementById('wizardSubmit');

  if (!modal || !addBtn) return;

  addBtn.addEventListener('click', () => {
    resetWizard();
    modal.classList.add('open');
  });

  const closeWizard = () => {
    modal.classList.remove('open');
    resetWizard();
  };

  if (closeBtn) closeBtn.addEventListener('click', closeWizard);
  modal.addEventListener('click', (e) => { if (e.target === modal) closeWizard(); });

  // Step navigation
  document.querySelectorAll('.wizard-next').forEach(btn => {
    btn.addEventListener('click', () => {
      const next = parseInt((btn as HTMLElement).getAttribute('data-next') || '1', 10);
      goToWizardStep(next);
    });
  });

  document.querySelectorAll('.wizard-prev').forEach(btn => {
    btn.addEventListener('click', () => {
      const prev = parseInt((btn as HTMLElement).getAttribute('data-prev') || '1', 10);
      goToWizardStep(prev);
    });
  });

  // Document upload
  document.querySelectorAll('.wizard-doc-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const el = btn as HTMLElement;
      const container = el.closest('.wizard-doc-upload');
      if (container?.classList.contains('uploaded')) return;
      el.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px!important;">check</span> Déposé';
      el.classList.add('uploaded');
      container?.classList.add('uploaded');
    });
  });

  // Submit — create client via API
  if (submitBtn) {
    submitBtn.addEventListener('click', async () => {
      const firstName = (document.getElementById('wiz-firstname') as HTMLInputElement)?.value?.trim();
      const lastName = (document.getElementById('wiz-lastname') as HTMLInputElement)?.value?.trim();

      if (!firstName || !lastName) {
        goToWizardStep(1);
        (document.getElementById('wiz-firstname') as HTMLInputElement)?.focus();
        return;
      }

      const orig = submitBtn.innerHTML;
      submitBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px!important;">sync</span> Création...';
      submitBtn.disabled = true;

      try {
        const email = (document.getElementById('wiz-email') as HTMLInputElement)?.value?.trim();
        const phone = (document.getElementById('wiz-phone') as HTMLInputElement)?.value?.trim();
        const address = (document.getElementById('wiz-address') as HTMLInputElement)?.value?.trim();
        const cp = (document.getElementById('wiz-cp') as HTMLInputElement)?.value?.trim();
        const city = (document.getElementById('wiz-city') as HTMLInputElement)?.value?.trim();

        await fetch('/api/clients', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            firstName,
            lastName,
            email: email || undefined,
            phone: phone || undefined,
            insuredAddress: address || undefined,
            insuredPostalCode: cp || undefined,
            insuredCity: city || undefined,
          }),
        });

        // Reload table
        await loadClientsIntoTable();

        submitBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px!important;">check</span> Client créé !';
        submitBtn.style.background = '#10b981';

        setTimeout(() => {
          closeWizard();
          submitBtn.innerHTML = orig;
          submitBtn.style.background = '';
          submitBtn.disabled = false;
        }, 1000);
      } catch (err) {
        submitBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px!important;">error</span> Erreur';
        submitBtn.style.background = '#ef4444';
        setTimeout(() => {
          submitBtn.innerHTML = orig;
          submitBtn.style.background = '';
          submitBtn.disabled = false;
        }, 2000);
      }
    });
  }
}

function goToWizardStep(step: number): void {
  document.querySelectorAll('.wizard-panel').forEach(p => p.classList.remove('active'));
  const panel = document.querySelector(`.wizard-panel[data-panel="${step}"]`);
  if (panel) panel.classList.add('active');

  document.querySelectorAll('.wizard-step').forEach(s => {
    const sStep = parseInt((s as HTMLElement).getAttribute('data-step') || '0', 10);
    s.classList.remove('active', 'completed');
    if (sStep === step) s.classList.add('active');
    else if (sStep < step) s.classList.add('completed');
  });
}

function resetWizard(): void {
  goToWizardStep(1);
  const form = document.getElementById('clientWizardForm') as HTMLFormElement | null;
  if (form) form.reset();
  document.querySelectorAll('.wizard-doc-upload').forEach(el => el.classList.remove('uploaded'));
  document.querySelectorAll('.wizard-doc-btn').forEach(el => {
    el.classList.remove('uploaded');
    el.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px!important;">upload</span> Déposer';
  });
}

/* ── Client Detail Panel ────────────────────────────── */

async function openClientDetail(clientId: string): Promise<void> {
  currentClientId = clientId;
  isEditing = false;

  // Fetch client with properties from API
  let client: any;
  try {
    const res = await fetch(`/api/clients/${encodeURIComponent(clientId)}`);
    if (res.ok) client = await res.json();
  } catch {}

  // Fallback: use cached/mock client
  if (!client) {
    const cached = getCachedClient(clientId);
    if (!cached) return;
    client = { ...cached };
  }

  // Hide tab-content panels, show detail panel
  document.querySelectorAll('.clients-tab-content').forEach(el => el.classList.remove('active'));
  const panel = document.getElementById('clientsDetailPanel');
  if (panel) panel.classList.add('active');

  const initials = (client.firstName?.[0] || '') + (client.lastName?.[0] || '');
  const statusLabel: Record<string, string> = { active: 'Actif', pending: 'En attente', suspended: 'Suspendu' };

  // Populate profile header
  const avatarEl = document.getElementById('cdpAvatar');
  if (avatarEl) avatarEl.textContent = initials;
  const nameEl = document.getElementById('cdpName');
  if (nameEl) nameEl.textContent = `${client.firstName || ''} ${client.lastName || ''}`;
  const refEl = document.getElementById('cdpRef') as HTMLElement | null;
  if (refEl) refEl.textContent = client.ref || client.id?.substring(0, 8) || '';

  const statusEl = document.getElementById('cdpStatus') as HTMLElement | null;
  if (statusEl) {
    statusEl.textContent = statusLabel[client.status as keyof typeof statusLabel] || client.status || '—';
    statusEl.className = 'cdp-status ' + (client.status || 'pending');
  }

  // Populate extended info
  const addressCity = [client.insuredAddress, client.insuredCity].filter(Boolean).join(', ');
  populateOverview({
    civility: client.civility || '',
    firstName: client.firstName || '',
    lastName: client.lastName || '',
    email: client.email || '',
    phone: client.phone || '',
    address: client.insuredAddress || '',
    cp: client.insuredPostalCode || '',
    city: client.insuredCity || '',
    nationality: 'Française',
    profession: '',
    dob: '',
    status: client.status || 'pending',
    addressCity,
    hasProperties: (client.properties?.length || 0) > 0,
  });

  // Populate form fields
  setInputValue('cdpFieldCivility', client.civility || 'M.');
  setInputValue('cdpFieldFirstname', client.firstName || '');
  setInputValue('cdpFieldLastname', client.lastName || '');
  setInputValue('cdpFieldEmail', client.email || '');
  setInputValue('cdpFieldPhone', client.phone || '');
  setInputValue('cdpFieldAddress', client.insuredAddress || '');
  setInputValue('cdpFieldCp', client.insuredPostalCode || '');
  setInputValue('cdpFieldCity', client.insuredCity || '');
  setInputValue('cdpFieldNationality', 'Française');
  setInputValue('cdpFieldProfession', '');
  setInputValue('cdpFieldDob', '');

  // Disable form fields (view mode)
  setFormFieldsDisabled(true);
  const formActions = document.getElementById('cdpFormActions');
  if (formActions) formActions.style.display = 'none';

  // Populate properties list (from client.properties if available)
  const propsList = document.getElementById('cdpContractsList');
  if (propsList) {
    const props = client.properties || [];
    if (props.length > 0) {
      propsList.innerHTML = props.map((p: any) => `
        <div class="cdp-contract-card">
          <span class="material-symbols-outlined cdp-contract-icon" style="background:#6366f11a;color:#6366f1;">home</span>
          <div class="cdp-contract-body">
            <span class="cdp-contract-name">${p.address || 'Adresse inconnue'}</span>
            <span class="cdp-contract-meta">
              <span>${p.city || ''}${p.dpeClass ? ' · DPE: ' + p.dpeClass : ''}</span>
            </span>
          </div>
        </div>
      `).join('');
    } else {
      propsList.innerHTML = '<p style="font-size:11px;color:var(--text-muted);padding:8px;">Aucun bien enregistré</p>';
    }
  }

  // Populate payment history (simplified — no payments table in backend yet)
  const historyBody = document.getElementById('cdpHistoryBody');
  if (historyBody) {
    historyBody.innerHTML = '<tr><td colspan="5" style="text-align:center;padding:16px;font-size:11px;color:var(--text-muted);">Historique des paiements — module à connecter</td></tr>';
  }

  // Load risk scores from assessments
  loadClientAssessments(clientId);

  // Reset tabs
  document.querySelectorAll('.cdp-tab-content').forEach(el => el.classList.remove('active'));
  document.querySelector('.cdp-tab-content[data-cdp-content="overview"]')?.classList.add('active');
  document.querySelectorAll('.cdp-tab').forEach(t => t.classList.remove('active'));
  document.querySelector('.cdp-tab[data-cdp-tab="overview"]')?.classList.add('active');
}

interface OverviewData {
  civility: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  address: string;
  cp: string;
  city: string;
  nationality: string;
  profession: string;
  dob: string;
  status: string;
  addressCity: string;
  hasProperties: boolean;
}

function populateOverview(data: OverviewData): void {
  setText('cdpOvCivility', data.civility);
  setText('cdpOvName', `${data.firstName} ${data.lastName}`);
  setText('cdpOvEmail', data.email || '—');
  setText('cdpOvPhone', data.phone || '—');
  setText('cdpOvAddress', data.addressCity || '—');

  const statusLabels: Record<string, string> = { active: 'Actif', pending: 'En attente', suspended: 'Suspendu' };
  const statusEl = document.getElementById('cdpOvStatus');
  if (statusEl) {
    statusEl.textContent = statusLabels[data.status] || data.status;
    (statusEl as HTMLElement).style.color = data.status === 'active' ? '#059669' : data.status === 'pending' ? '#d97706' : '#dc2626';
  }

  // Simplified contract summary
  setText('cdpOvTotalContracts', data.hasProperties ? '1' : '0');
  setText('cdpOvActiveContracts', data.hasProperties ? '1' : '0');
  setText('cdpOvPendingContracts', '0');
  setText('cdpOvAnnualPremium', '—');

  // Also update detail panel stats header
  setText('cdpStatContracts', data.hasProperties ? '1' : '0');
  setText('cdpStatActive', data.hasProperties ? '1' : '0');
  setText('cdpStatPending', '0');
  setText('cdpStatPremium', '—');

  // Property list (mini)
  const contractsList = document.getElementById('cdpOvContractsList');
  if (contractsList) {
    if (data.hasProperties) {
      contractsList.innerHTML = `
        <div class="cdp-ov-contract-row">
          <span class="material-symbols-outlined cdp-ov-contract-icon" style="color:#6366f1;">home</span>
          <div class="cdp-ov-contract-info">
            <span class="cdp-ov-contract-name">Bien assuré</span>
            <span class="cdp-ov-contract-ref">${data.addressCity}</span>
          </div>
          <span class="cdp-ov-contract-status" style="color:#059669;">Actif</span>
        </div>`;
    } else {
      contractsList.innerHTML = '<p style="font-size:11px;color:var(--text-muted);padding:8px;">Aucun bien enregistré</p>';
    }
  }

  // Payments placeholder
  const paymentsList = document.getElementById('cdpOvPaymentsList');
  if (paymentsList) {
    paymentsList.innerHTML = '<p style="font-size:11px;color:var(--text-muted);padding:8px;">Historique des paiements — à venir</p>';
  }
}

/* ── Populate risk scores from assessments ─────────────────── */

async function loadClientAssessments(clientId: string): Promise<void> {
  try {
    // Fetch assessments for this client's properties
    const clientRes = await fetch(`/api/clients/${encodeURIComponent(clientId)}`);
    if (!clientRes.ok) return;
    const clientData = await clientRes.json();
    const props = clientData?.properties || [];
    if (props.length === 0) return;

    // Fetch all assessments from API
    const assRes = await fetch('/api/assessments');
    if (!assRes.ok) return;
    const assessments = await assRes.json();

    // Filter assessments for this client's properties
    const propIds = new Set(props.map((p: any) => p.id));
    const clientAssessments = assessments.filter((a: any) => propIds.has(a.propertyId));

    if (clientAssessments.length === 0) return;

    // Take the most recent assessment
    const latest = clientAssessments.sort((a: any, b: any) =>
      new Date(b.createdAt || 0).getTime() - new Date(a.createdAt || 0).getTime()
    )[0];

    // Try both panel IDs (assureur and admin)
    let scoresEl = document.getElementById('cdpOvScores');
    if (!scoresEl) scoresEl = document.getElementById('cdpOvScoresAdmin');
    if (!scoresEl) return;

    const scores = [
      { key: 'inondation', label: 'Inondation', val: latest.inondationScore, color: '#3b82f6' },
      { key: 'rga', label: 'RGA', val: latest.rgaScore, color: '#f59e0b' },
      { key: 'tempete', label: 'Tempête', val: latest.tempeteScore, color: '#8b5cf6' },
      { key: 'incendie', label: 'Incendie', val: latest.incendieScore, color: '#ef4444' },
      { key: 'seisme', label: 'Séisme', val: latest.seismeScore, color: '#6366f1' },
    ];

    const globalScore = latest.globalScore || 0;
    const globalColor = globalScore >= 70 ? '#ef4444' : globalScore >= 50 ? '#f59e0b' : globalScore >= 30 ? '#3b82f6' : '#10b981';

    scoresEl.innerHTML = `
      <div class="cdp-overview-score-global" style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--border-color);margin-bottom:8px;">
        <div style="width:40px;height:40px;border-radius:50%;background:${globalColor}20;display:flex;align-items:center;justify-content:center;">
          <span style="font-size:16px;font-weight:700;color:${globalColor};">${globalScore}</span>
        </div>
        <div>
          <div style="font-size:11px;font-weight:600;color:var(--text-primary);">Score global</div>
          <div style="font-size:10px;color:var(--text-muted);">${latest.createdAt ? new Date(latest.createdAt).toLocaleDateString('fr-FR') : 'Date inconnue'}</div>
        </div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;">
        ${scores.map(s => {
          const v = s.val || 0;
          const c = v >= 70 ? '#ef4444' : v >= 50 ? '#f59e0b' : v >= 30 ? '#3b82f6' : '#10b981';
          return `<div style="display:flex;justify-content:space-between;padding:4px 6px;background:var(--bg-panel);border-radius:4px;font-size:10px;">
            <span style="color:var(--text-secondary);">${s.label}</span>
            <span style="color:${c};font-weight:600;">${v}</span>
          </div>`;
        }).join('')}
      </div>`;
  } catch {
    // Silent — scores card stays as "Aucune évaluation"
  }
}

/* ── Event delegation for table rows (avoids re-wiring on reload) ── */

let tableDelegationWired = false;

function wireTableDelegation(tbody: HTMLElement): void {
  // Only wire the delegation listener once
  if (tableDelegationWired) return;
  tableDelegationWired = true;

  tbody.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;
    const actionBtn = target.closest('.clients-action-btn') as HTMLElement | null;
    const row = target.closest('.clients-table-row') as HTMLElement | null;
    if (!row) return;
    const clientId = row.getAttribute('data-client');
    if (!clientId) return;

    if (actionBtn) {
      const action = actionBtn.getAttribute('data-action');
      if (action === 'view') {
        openClientDetail(clientId);
      } else if (action === 'edit') {
        openClientDetail(clientId);
        setTimeout(() => {
          isEditing = true;
          setFormFieldsDisabled(false);
          const formActions = document.getElementById('cdpFormActions');
          if (formActions) formActions.style.display = 'flex';
          const editBtn = document.getElementById('cdpEditToggle');
          if (editBtn) editBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px!important;">close</span> Annuler';
        }, 300);
      } else if (action === 'status') {
        openClientDetail(clientId);
        setTimeout(() => {
          const toggle = document.getElementById('cdpStatusToggle');
          if (toggle) toggle.click();
        }, 400);
      } else if (action === 'more') {
        const name = row.querySelector('.clients-table-name')?.textContent || 'Client';
        showInfo(`Options pour ${name} — module à implémenter.`);
      }
    } else {
      // Row click → open detail
      openClientDetail(clientId);
    }
  });
}

/* ── Helpers ────────────────────────────────────────── */

function setText(id: string, text: string): void {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function setInputValue(id: string, value: string): void {
  const el = document.getElementById(id) as HTMLInputElement | HTMLSelectElement | null;
  if (el) el.value = value;
}

function closeClientDetail(): void {
  currentClientId = null;
  isEditing = false;
  const panel = document.getElementById('clientsDetailPanel');
  if (panel) panel.classList.remove('active');
  document.querySelector('.clients-tab-content[data-content="info"]')?.classList.add('active');
  setFormFieldsDisabled(true);
  const formActions = document.getElementById('cdpFormActions');
  if (formActions) formActions.style.display = 'none';
}

function setFormFieldsDisabled(disabled: boolean): void {
  document.querySelectorAll('.cdp-field input, .cdp-field select').forEach(el => {
    if (disabled) el.setAttribute('disabled', 'disabled');
    else el.removeAttribute('disabled');
  });
}

function toggleEditMode(): void {
  isEditing = !isEditing;
  setFormFieldsDisabled(!isEditing);
  const formActions = document.getElementById('cdpFormActions');
  if (formActions) formActions.style.display = isEditing ? 'flex' : 'none';
  const editBtn = document.getElementById('cdpEditToggle');
  if (!editBtn) return;
  if (isEditing) {
    editBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px!important;">close</span> Annuler';
  } else {
    editBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px!important;">edit</span> Modifier';
  }
}

async function saveClientInfo(): Promise<void> {
  if (!currentClientId) return;

  const data: Record<string, string> = {
    civility: getInputValue('cdpFieldCivility'),
    firstName: getInputValue('cdpFieldFirstname'),
    lastName: getInputValue('cdpFieldLastname'),
    email: getInputValue('cdpFieldEmail'),
    phone: getInputValue('cdpFieldPhone'),
    insuredAddress: getInputValue('cdpFieldAddress'),
    insuredPostalCode: getInputValue('cdpFieldCp'),
    insuredCity: getInputValue('cdpFieldCity'),
  };

  try {
    await fetch(`/api/clients/${encodeURIComponent(currentClientId)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    // Update header
    const nameEl = document.getElementById('cdpName');
    if (nameEl) nameEl.textContent = `${data.firstName || ''} ${data.lastName || ''}`;

    // Update table row
    const row = document.querySelector(`.clients-table-row[data-client="${currentClientId}"]`);
    if (row) {
      const nameCell = row.querySelector('.clients-table-name');
      if (nameCell) nameCell.textContent = `${data.firstName || ''} ${data.lastName || ''}`;
      const emailCell = row.querySelector('.clients-table-email');
      if (emailCell) emailCell.textContent = data.email || '—';
    }
  } catch {
    // Silent fail for demo
  }

  isEditing = false;
  setFormFieldsDisabled(true);
  const formActions = document.getElementById('cdpFormActions');
  if (formActions) formActions.style.display = 'none';
  const editBtn = document.getElementById('cdpEditToggle');
  if (editBtn) {
    editBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px!important;">edit</span> Modifier';
  }

  // Flash feedback
  const saveBtn = document.getElementById('cdpSaveBtn');
  if (saveBtn) {
    const orig = saveBtn.innerHTML;
    saveBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px!important;">check</span> Enregistré !';
    saveBtn.style.background = '#10b981';
    setTimeout(() => {
      saveBtn.innerHTML = orig;
      saveBtn.style.background = '';
    }, 1200);
  }
}

function getInputValue(id: string): string {
  const el = document.getElementById(id) as HTMLInputElement | HTMLSelectElement | null;
  return el?.value?.trim() || '';
}

/* ── Status Toggle ──────────────────────────────────── */

function setupStatusToggle(): void {
  const toggle = document.getElementById('cdpStatusToggle');
  const dropdown = document.getElementById('cdpStatusDropdown');
  const menu = document.getElementById('cdpStatusMenu');
  if (!toggle || !dropdown || !menu) return;

  toggle.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdown.classList.toggle('open');
  });

  document.addEventListener('click', (e) => {
    if (!dropdown.contains(e.target as Node)) {
      dropdown.classList.remove('open');
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') dropdown.classList.remove('open');
  });

  menu.querySelectorAll('.cdp-status-option').forEach(opt => {
    opt.addEventListener('click', async () => {
      const newStatus = (opt as HTMLElement).getAttribute('data-status');
      if (!newStatus || !currentClientId) return;
      dropdown.classList.remove('open');
      await changeClientStatus(currentClientId, newStatus);
    });
  });
}

async function changeClientStatus(clientId: string, newStatus: string): Promise<void> {
  // Update via API
  try {
    await fetch(`/api/clients/${encodeURIComponent(clientId)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    });
  } catch {}

  // Update detail panel header
  const statusLabels: Record<string, string> = { active: 'Actif', pending: 'En attente', suspended: 'Suspendu' };
  const statusEl = document.getElementById('cdpStatus');
  if (statusEl) {
    statusEl.textContent = statusLabels[newStatus] || newStatus;
    statusEl.className = 'cdp-status ' + newStatus;
  }

  // Update table row
  const row = document.querySelector(`.clients-table-row[data-client="${clientId}"]`);
  if (row) {
    const statusCell = row.querySelector('.clients-table-status');
    if (statusCell) {
      statusCell.textContent = statusLabels[newStatus] || newStatus;
      statusCell.className = 'clients-table-status ' + newStatus;
    }
  }

  // Flash feedback
  if (statusEl) {
    statusEl.style.transition = 'all 0.15s ease';
    statusEl.style.transform = 'scale(1.05)';
    setTimeout(() => { statusEl.style.transform = ''; }, 200);
  }
}

/* ── Client Table Actions ───────────────────────────── */

function setupStaticActions(): void {
  // Called once from initClients — wires static elements that never change
  setupStatusToggle();

  const backBtn = document.getElementById('cdpBackBtn');
  if (backBtn) backBtn.addEventListener('click', closeClientDetail);

  // Évaluer ce bien → pass propertyId via sessionStorage → navigate to Risk Hub
  const evalBtn = document.getElementById('cdpEvaluateBtn');
  if (evalBtn) {
    evalBtn.addEventListener('click', () => {
      if (!currentClientId) return;
      fetch(`/api/clients/${encodeURIComponent(currentClientId)}`)
        .then(r => r.ok ? r.json() : null)
        .then(clientData => {
          const props = clientData?.properties || [];
          if (props.length > 0) {
            sessionStorage.setItem('assureur_property_id', props[0].id);
            sessionStorage.setItem('assureur_client_id', currentClientId);
          } else {
            sessionStorage.removeItem('assureur_property_id');
            sessionStorage.setItem('assureur_client_id', currentClientId);
          }
          import('../../router.js').then(({ navigateTo }) => {
            navigateTo('property-risk');
          });
        })
        .catch(() => {
          import('../../router.js').then(({ navigateTo }) => {
            navigateTo('property-risk');
          });
        });
    });
  }

  // Assign expert button
  const assignBtn = document.getElementById('cdpAssignExpertBtn');
  if (assignBtn) {
    assignBtn.addEventListener('click', async () => {
      if (!currentClientId) return;

      const clientName = document.getElementById('cdpName')?.textContent || 'Client';
      const expertEmail = await showPrompt({
        title: 'Assigner un expert',
        content: `Assigner un expert pour évaluer le bien de ${clientName}`,
        inputLabel: 'Email de l\'expert',
        inputPlaceholder: 'expert@previa.fr',
        inputValue: 'expert@previa.fr',
      });

      if (!expertEmail) return;

      try {
        const res = await fetch(`/api/clients/${encodeURIComponent(currentClientId)}`);
        if (!res.ok) {
          showError('Impossible de récupérer les données du client');
          return;
        }
        const clientData = await res.json();
        const props = clientData?.properties || [];
        const propertyId = props.length > 0 ? props[0].id : '';
        const address = props.length > 0 ? (props[0].address || '') : '';
        const city = props.length > 0 ? (props[0].city || '') : '';

        const assignRes = await fetch('/api/expert/assign', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            clientId: currentClientId,
            clientName,
            propertyId,
            address,
            city,
            assignedTo: expertEmail,
            assignedByName: 'Assureur',
            notes: '',
          }),
        });

        if (assignRes.ok) {
          showSuccess(`Expert ${expertEmail} assigné avec succès ! La mission est disponible dans l'espace Expert.`);
        } else {
          const err = await assignRes.json().catch(() => ({}));
          showError(err.error || 'Impossible d\'assigner l\'expert');
        }
      } catch {
        showError('Erreur réseau lors de l\'assignation');
      }
    });
  }

  const editBtn = document.getElementById('cdpEditToggle');
  if (editBtn) editBtn.addEventListener('click', toggleEditMode);

  const saveBtn = document.getElementById('cdpSaveBtn');
  if (saveBtn) saveBtn.addEventListener('click', saveClientInfo);

  const cancelBtn = document.getElementById('cdpCancelBtn');
  if (cancelBtn) {
    cancelBtn.addEventListener('click', () => {
      isEditing = false;
      setFormFieldsDisabled(true);
      const formActions = document.getElementById('cdpFormActions');
      if (formActions) formActions.style.display = 'none';
      const editBtn = document.getElementById('cdpEditToggle');
      if (editBtn) editBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size:16px!important;">edit</span> Modifier';
      if (currentClientId) openClientDetail(currentClientId);
    });
  }

  document.querySelectorAll('.cdp-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const target = (tab as HTMLElement).getAttribute('data-cdp-tab');
      if (!target) return;
      document.querySelectorAll('.cdp-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      document.querySelectorAll('.cdp-tab-content').forEach(el => el.classList.remove('active'));
      document.querySelector(`.cdp-tab-content[data-cdp-content="${target}"]`)?.classList.add('active');
    });
  });

  document.querySelectorAll('.clients-upload-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const orig = (btn as HTMLElement).innerHTML;
      (btn as HTMLElement).innerHTML = '<span class="material-symbols-outlined" style="font-size:16px!important;">check_circle</span> Déposé';
      setTimeout(() => { (btn as HTMLElement).innerHTML = orig; }, 1200);
    });
  });

  document.querySelectorAll('.clients-contract-view').forEach(btn => {
    btn.addEventListener('click', () => {
      showInfo('Ouverture du contrat... (module à implémenter)');
    });
  });
}
