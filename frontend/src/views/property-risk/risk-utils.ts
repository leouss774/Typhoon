/**
 * Risk Hub Shared Utilities
 * ==========================
 * 
 * Extracted from property-risk.ts to avoid circular dependency
 * with risk-expert-form.ts. Both modules import from here.
 */

/* ── Tab Navigation ────────────────────────────────────── */

export function navigateToTab(tabKey: string): void {
  const headerTabs = document.getElementById('headerTabs');
  if (headerTabs) {
    const btn = headerTabs.querySelector(`.tab-btn[data-tab="${tabKey}"]`) as HTMLButtonElement | null;
    if (btn) btn.click();
  }
}

/* ── Toast Notification ────────────────────────────────── */

export function showToast(html: string, durationMs: number = 4000): void {
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

/* ── Evaluate Tab Refresh ──────────────────────────────── */

export function triggerEvaluateRefresh(): void {
  window.dispatchEvent(new CustomEvent('previa:evaluate'));
}

/* ── Evaluate Metrics ─────────────────────────────────── */

/** Import this alongside the real renderEvaluateMetrics from property-risk.ts */
export type { PerilScores } from './risk-state.js';
