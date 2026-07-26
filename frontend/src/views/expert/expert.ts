/**
 * Expert view module — lightweight lifecycle for expert missions dashboard.
 * Fetches real assignments from API and displays them as mission cards.
 */

let initialized = false;

export function initExpertMissions(): void {
  if (initialized) return;
  initialized = true;
  loadExpertMissions();
}

export function destroyExpertMissions(): void {
  initialized = false;
}

async function loadExpertMissions(): Promise<void> {
  const grid = document.getElementById('expertMissionsGrid');
  if (!grid) return;

  try {
    // Fetch all missions from API
    const res = await fetch('/api/expert/missions');
    let missions: Array<{
      id: string;
      clientId: string;
      clientName: string;
      address: string;
      city: string;
      assignedTo: string;
      status: 'pending' | 'in_progress' | 'completed';
      createdAt: string;
    }> = [];

    if (res.ok) {
      missions = await res.json();
    }

    if (missions.length === 0) {
      // Fallback: show empty state with a helpful message
      grid.innerHTML = `
        <div class="dashboard-card" style="padding:32px;display:flex;flex-direction:column;align-items:center;gap:12px;text-align:center;grid-column:1/-1;">
          <span class="material-symbols-outlined" style="font-size:48px;color:var(--text-muted);opacity:0.3;">assignment_turned_in</span>
          <p style="font-size:13px;color:var(--text-secondary);">Aucune mission pour le moment</p>
          <p style="font-size:11px;color:var(--text-muted);">Les missions apparaîtront ici après qu'un assureur vous les ait assignées.</p>
        </div>`;
      return;
    }

    const statuses: Record<string, { label: string; color: string; textColor: string }> = {
      pending: { label: 'En attente', color: 'rgba(245,158,11,0.15)', textColor: '#f59e0b' },
      in_progress: { label: 'En cours', color: 'rgba(99,102,241,0.15)', textColor: '#6366f1' },
      completed: { label: 'Terminée', color: 'rgba(16,185,129,0.15)', textColor: '#10b981' },
    };

    grid.innerHTML = missions.map(m => {
      const s = statuses[m.status] || statuses.pending;
      const addr = [m.address, m.city].filter(Boolean).join(', ') || 'Adresse non renseignée';
      return `
        <div class="dashboard-card" style="padding:16px;display:flex;flex-direction:column;gap:10px;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div>
              <div style="font-size:14px;font-weight:600;">${escapeHtml(m.clientName)}</div>
              <div style="font-size:12px;color:var(--text-muted);">${escapeHtml(addr)}</div>
            </div>
            <span style="font-size:10px;color:var(--text-muted);">${escapeHtml(m.assignedTo)}</span>
          </div>
          <div style="display:flex;gap:8px;font-size:11px;color:var(--text-secondary);">
            <span class="material-symbols-outlined" style="font-size:14px;">calendar_today</span>
            <span>Assignée le ${new Date(m.createdAt).toLocaleDateString('fr-FR')}</span>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center;padding-top:8px;border-top:1px solid var(--border-color);">
            <span style="font-size:11px;padding:3px 10px;border-radius:12px;background:${s.color};color:${s.textColor};font-weight:500;">${s.label}</span>
            <button class="risk-btn primary" style="height:28px;font-size:11px;padding:0 12px;" data-mission-id="${m.id}" data-action="start">
              ${m.status === 'pending' ? 'Démarrer' : m.status === 'in_progress' ? 'Continuer' : 'Voir'}
            </button>
          </div>
        </div>
      `;
    }).join('');

    // Wire action buttons
    grid.querySelectorAll('[data-action="start"]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const missionId = (btn as HTMLElement).getAttribute('data-mission-id');
        if (!missionId) return;

        // Toggle status: pending → in_progress → completed
        const card = (btn as HTMLElement).closest('.dashboard-card');
        const statusEl = card?.querySelector(':scope > div:last-child > span:first-child');
        const currentStatus = statusEl?.textContent || '';

        let newStatus: string;
        if (currentStatus === 'En attente') newStatus = 'in_progress';
        else if (currentStatus === 'En cours') newStatus = 'completed';
        else return;

        try {
          const res = await fetch(`/api/expert/missions/${missionId}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus }),
          });
          if (res.ok) {
            loadExpertMissions(); // Reload
          }
        } catch {}
      });
    });

  } catch (err) {
    console.warn('[Expert] Failed to load missions:', err);
  }

  // Setup filter (one-time)
  const filter = document.getElementById('expertMissionFilter');
  if (filter && !filter.getAttribute('data-filter-wired')) {
    filter.setAttribute('data-filter-wired', 'true');
    filter.addEventListener('change', () => {
      const val = (filter as HTMLSelectElement).value;
      const cards = grid.querySelectorAll('[data-mission-id]');
      cards.forEach(card => {
        const cardEl = (card as HTMLElement).closest('.dashboard-card') as HTMLElement | null;
        if (!cardEl) return;
        if (val === 'all') {
          cardEl.style.display = '';
        } else {
          const statusMap: Record<string, string> = { pending: 'En attente', in_progress: 'En cours', completed: 'Terminée' };
          const label = statusMap[val] || '';
          const statusEl = cardEl.querySelector(':scope > div:last-child > span:first-child');
          cardEl.style.display = statusEl?.textContent === label ? '' : 'none';
        }
      });
    });
  }
}

function escapeHtml(str: string): string {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
