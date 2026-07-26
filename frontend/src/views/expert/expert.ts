/**
 * Expert view module — lightweight lifecycle for expert missions dashboard.
 */
import { fetchClientsFromApi } from '../../api/data-service.js';

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
  try {
    const clients = await fetchClientsFromApi().catch(() => []);
    const grid = document.getElementById('expertMissionsGrid');
    if (!grid) return;

    // Create sample mission cards from client data
    if (clients.length > 0) {
      const riskLevels = ['Haut', 'Modéré', 'Faible'];
      const riskColors = ['#ef4444', '#f59e0b', '#10b981'];
      const statuses = [
        { label: 'En attente', color: 'rgba(245,158,11,0.15)', textColor: '#f59e0b' },
        { label: 'En cours', color: 'rgba(99,102,241,0.15)', textColor: '#6366f1' },
        { label: 'Terminée', color: 'rgba(16,185,129,0.15)', textColor: '#10b981' },
      ];

      grid.innerHTML = clients.slice(0, 6).map((c, i) => {
        const riskIdx = i % 3;
        const statusIdx = i % 3;
        const addresses = ['8 Rue de la Paix', '15 Bd Haussmann', '34 Rue de Rivoli', '5 Rue de Rennes', '12 Rue Matabiau', '7 Rue du Bac'];
        const address = c.insuredAddress || addresses[i] || 'Adresse inconnue';
        const city = c.insuredCity || '';

        return `
          <div class="dashboard-card" style="padding:16px;display:flex;flex-direction:column;gap:10px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
              <div>
                <div style="font-size:14px;font-weight:600;">${escapeHtml(c.firstName)} ${escapeHtml(c.lastName)}</div>
                <div style="font-size:12px;color:var(--text-muted);">${escapeHtml(address)}${city ? ' · ' + escapeHtml(city) : ''}</div>
              </div>
              <span style="font-size:11px;padding:3px 10px;border-radius:12px;background:${riskColors[riskIdx]}15;color:${riskColors[riskIdx]};font-weight:500;">${riskLevels[riskIdx]} risque</span>
            </div>
            <div style="display:flex;gap:8px;font-size:11px;color:var(--text-secondary);">
              <span class="material-symbols-outlined" style="font-size:14px;">calendar_today</span>
              <span>Soumis le ${new Date(Date.now() - i * 86400000).toLocaleDateString('fr-FR')}</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding-top:8px;border-top:1px solid var(--border-color);">
              <span style="font-size:11px;padding:3px 10px;border-radius:12px;background:${statuses[statusIdx].color};color:${statuses[statusIdx].textColor};font-weight:500;">${statuses[statusIdx].label}</span>
              <button class="risk-btn primary" style="height:28px;font-size:11px;padding:0 12px;" onclick="alert('Démarrer mission — à implémenter')">Démarrer</button>
            </div>
          </div>
        `;
      }).join('');
    }

    // Setup filter
    const filter = document.getElementById('expertMissionFilter');
    if (filter) {
      filter.addEventListener('change', () => {
        const val = (filter as HTMLSelectElement).value;
        const cards = grid.querySelectorAll('.dashboard-card');
        // Reset all cards to visible first
        cards.forEach(card => { (card as HTMLElement).style.display = ''; });
        if (val !== 'all') {
          const map: Record<string, string> = { pending: 'En attente', in_progress: 'En cours', completed: 'Terminée' };
          cards.forEach(card => {
            const statusEl = card.querySelector(':scope > div:last-child > span:first-child');
            if (statusEl) {
              const statusText = statusEl.textContent || '';
              if (statusText !== map[val]) {
                (card as HTMLElement).style.display = 'none';
              }
            }
          });
        }
      });
    }
  } catch (err) {
    console.warn('[Expert] Failed to load missions:', err);
  }
}

function escapeHtml(str: string): string {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
